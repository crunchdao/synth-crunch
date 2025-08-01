import asyncio
import typing

import bittensor as bt
from model_runner_client.grpc.generated.commons_pb2 import (KwArgument,
                                                            Variant,
                                                            VariantType)
from model_runner_client.model_concurrent_runners.dynamic_subclass_model_concurrent_runner import \
    DynamicSubclassModelConcurrentRunner
from model_runner_client.utils.datatype_transformer import (detect_data_type,
                                                            encode_data)
from synth.base.miner import BaseMinerNeuron
from synth.miner.simulations import get_asset_price
from synth.protocol import Simulation


class Miner(BaseMinerNeuron):

    def __init__(
        self,
        crunch_id: str = "synth",
        host: str = "localhost",
        port: int = 9091,
        base_classname: str = 'synth_crunch.SynthMiner',
        timeout: int = 10,
    ):
        super(Miner, self).__init__(config=None)

        self.concurrent_runner = DynamicSubclassModelConcurrentRunner(
            timeout=timeout,
            crunch_id=crunch_id,
            host=host,
            port=port,
            base_classname=base_classname
        )

        self.concurrent_runner_loop = asyncio.new_event_loop()

        self.concurrent_runner_loop.run_until_complete(self.concurrent_runner.init())
        self.concurrent_runner_loop.create_task(self.concurrent_runner.sync())

    async def forward_miner(self, synapse: Simulation) -> Simulation:
        input = synapse.simulation_input
        bt.logging.info(f"Received prediction request from: {synapse.dendrite.hotkey} for timestamp: {input.start_time}")

        asset = input.asset

        current_price = get_asset_price(asset)
        current_price_type = detect_data_type(current_price)

        sigma = 0.1  # no provided via input??

        results = await await_from_another_loop(
            self.concurrent_runner.call(
                method_name='generate_simulations',
                arguments=(
                    None,
                    [
                        KwArgument(
                            keyword="asset",
                            data=Variant(type=VariantType.STRING, value=encode_data(VariantType.STRING, asset)),
                        ),
                        KwArgument(
                            keyword="current_price",
                            data=Variant(type=current_price_type, value=encode_data(current_price_type, current_price)),
                        ),
                        KwArgument(
                            keyword="start_time",
                            data=Variant(type=VariantType.STRING, value=encode_data(VariantType.STRING, input.start_time)),
                        ),
                        KwArgument(
                            keyword="time_increment",
                            data=Variant(type=VariantType.INT, value=encode_data(VariantType.INT, input.time_increment)),
                        ),
                        KwArgument(
                            keyword="time_length",
                            data=Variant(type=VariantType.INT, value=encode_data(VariantType.INT, input.time_length)),
                        ),
                        KwArgument(
                            keyword="num_simulations",
                            data=Variant(type=VariantType.INT, value=encode_data(VariantType.INT, input.num_simulations)),
                        ),
                        KwArgument(
                            keyword="sigma",
                            data=Variant(type=VariantType.DOUBLE, value=encode_data(VariantType.DOUBLE, sigma)),
                        ),
                    ],
                ),
            ),
            self.concurrent_runner_loop
        )

        for model_runner, model_predict_result in results.items():
            print(f"{model_runner.model_id}: {model_predict_result}")

        # TODO do average of results
        synapse.simulation_output = next(iter(results.values())).result if len(results) else None

        return synapse

    async def blacklist(self, synapse: Simulation) -> typing.Tuple[bool, str]:
        if synapse.dendrite is None or synapse.dendrite.hotkey is None:
            return True, "Missing dendrite or hotkey"

        # HACK: Only allow Enzo's registered validator
        # TODO: Use blacklist exemptions instead (discovered after)
        if synapse.dendrite.hotkey != "5Dz6WvbgM749zdv9pk6RPFcgJPv7fB7vSNnR1AJ518wtkKcs":
            bt.logging.warning(f"Received a request from another validator: {synapse.dendrite.hotkey}")
            return True, "not my own validator"

        # HACK: Remove most of the blacklist logic
        return False, "Hotkey recognized!"

    async def priority(self, synapse: Simulation) -> float: return 0.0  # HACK: Don't care for now
    def save_state(self): pass
    def load_state(self): pass
    def set_weights(self): pass
    async def forward_validator(self): pass


async def await_from_another_loop(
    coro: typing.Awaitable,
    target_loop: asyncio.AbstractEventLoop
) -> typing.Any:
    """
    Require to have a way to await from 2 different event loops without blocking the other...
    - The loop from the webserver (fastapi + unicorn), which cannot be either created in advance or get a reference to
    - The loop from the model runner client

    This basically create a future in the current loop, and then waits for it.
    In paralle, we schedule a task in the other loop that will fill the future with the result of the coroutine.
    Terrible design...
    """

    my_loop = asyncio.get_running_loop()

    if target_loop is my_loop:
        return await coro

    my_target = my_loop.create_future()

    async def wait_target():
        try:
            result = await coro
        except Exception as exception:
            my_loop.call_soon_threadsafe(my_target.set_exception, (exception))
        else:
            my_loop.call_soon_threadsafe(my_target.set_result, (result))

    # "create_task" instead of "call_soon_threadsafe" because it would always forget the reference (gc)...
    # I hope it will not cause any issues, *foreshadowing*
    target_loop.create_task(wait_target())
    return await my_target


def main():
    with Miner() as miner:
        miner.run_in_background_thread()
        miner.concurrent_runner_loop.run_forever()
