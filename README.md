# Synth on CrunchDAO

Participate to the [Synth Subnet](https://github.com/mode-network/synth-subnet) directly via the CrunchDAO Platform, making it easier to have your code enter the protocol at no cost!

- [Synth on CrunchDAO](#synth-on-crunchdao)
- [Install](#install)
- [Usage](#usage)
  - [Your first model](#your-first-model)
  - [Test it locally](#test-it-locally)
- [Coordinating everything locally](#coordinating-everything-locally)
  - [Run the Model Orchestrator](#run-the-model-orchestrator)
  - [Run the Synth Validator](#run-the-synth-validator)
  - [Run the Synth Miner (via our CLI)](#run-the-synth-miner-via-our-cli)
  - [Trigger a Simulation](#trigger-a-simulation)

# Install

<!-- TODO Publish on PyPI and update the command -->

```bash
pip install git+https://github.com/crunchdao/synth-crunch.git
```

# Usage

## Your first model

```python
# Import the types
from synth_crunch import SynthMiner, Asset

# Import baseline functions
from synth_crunch.baseline import simulate_crypto_price_paths, convert_prices_to_time_format


class MyMiner(SynthMiner):

    def __init__(self):
        # Initialize your state in the constructor:
        # - load your model
        # - warmup your code

        pass

    def generate_simulations(
        self,
        asset: Asset,  # can only be "BTC", "ETH", "XAU" or "SOL"
        current_price: float,
        start_time: str,
        time_increment: int,
        time_length: int,
        num_simulations: int,
        sigma: float,
    ) -> list[list[dict[str, Any]]]:
        """
        Generate simulated price paths.

        Parameters:
            asset (str): The asset to simulate.
            current_price (float): The current price of the asset to simulate.
            start_time (str): The start time of the simulation. Defaults to current time.
            time_increment (int): Time increment in seconds.
            time_length (int): Total time length in seconds.
            num_simulations (int): Number of simulation runs.
            sigma (float): Standard deviation of the simulated price path.

        Returns:
            numpy.ndarray: Simulated price paths.
        """

        if start_time == "":
            raise ValueError("Start time must be provided.")

        if asset == "BTC":
            sigma *= 3
        elif asset == "ETH":
            sigma *= 1.25
        elif asset == "XAU":
            sigma *= 0.5
        elif asset == "SOL":
            sigma *= 0.75

        simulations = simulate_crypto_price_paths(
            current_price=current_price,
            time_increment=time_increment,
            time_length=time_length,
            num_simulations=num_simulations,
            sigma=sigma,
        )

        predictions = convert_prices_to_time_format(
            prices=simulations.tolist(),
            start_time=start_time,
            time_increment=time_increment,
        )

        return predictions
```

## Test it locally

<!-- TODO How should we do local testing? -->
<!--
    Via an inline tool?
    Via a cli (difficult if in notebook)?
    With with data, history from Pyth?
    Also use history to score it locally?
-->

# Coordinating everything locally

Every program must be run in a separate terminal as they are long-lived process.

## Run the Model Orchestrator

Run the [model orchestrator](https://github.com/crunchdao/model-orchestrator/) locally:

1. Run the orchestrator once and quit it to have the default configuration:

```bash
model-orchestrator dev
```

2. Update `orchestrator.dev.yml` with:

```yaml
crunches:
- id: "synth"
name: "synth"
infrastructure:
    zone: "local"
```

3. Import a dummy model in `storage/submissions/1`:
   - For `main.py`, take the example [from above](#your-first-model)
   - For the `requirements.txt`:

<!-- TODO Replace with correct name when package is available on PyPI -->
```python
synth-crunch @ git+https://github.com/crunchdao/synth-crunch.git
```

4. Update the desired state in `models.dev.yml` for the only model to `RUNNING`.

5. Run the orchestrator:

```bash
model-orchestrator dev
```

## Run the Synth Validator

Run the [Synth Validator](https://github.com/crunchdao/synth-subnet-prototype/) locally:

1. Clone the forked repository:

```bash
git clone git@github.com:crunchdao/synth-subnet-prototype.git
cd synth-subnet-prototype
```

2. Follow [part of the tutorial](https://github.com/crunchdao/synth-subnet-prototype/blob/main/docs/miner_tutorial.md) to have it installed and with generate the keys.

3. Run the validator:

```bash
python3 neurons/validator.py --network test --netuid 247 --logging.debug --logging.trace --subtensor.network test --wallet.name validator --wallet.hotkey default --neuron.axon_off true --ewma.half_life_days 5 --ewma.cutoff_days 10 --softmax.beta -0.1
```

> [!NOTE]
> The fork has been hacked to only work with [@Caceresenzo](https://github.com/Caceresenzo)'s keys which have been hardcoded.

## Run the Synth Miner (via our CLI)

Run the Synth Miner **via our CLI** locally:

1. Clone the repository:

<!-- TODO Publish on PyPI and remove the command? -->
```bash
git clone git@github.com:crunchdao/synth-crunch.git
cd synth-crunch
```

2. Install the Python package with the `infra` extras.

<!-- TODO Publish on PyPI and update the command -->
```bash
pip install -e '.[infra]'
```

3. Run the miner:

```bash
synth-crunch infra --netuid 247 --logging.debug --logging.trace --subtensor.network test --wallet.name miner --wallet.hotkey default --axon.port 8091 --blacklist.validator_min_stake 1
```

> [!NOTE]
> Again, the code has been hacked to only work with [@Caceresenzo](https://github.com/Caceresenzo)'s keys which have been hardcoded.

## Trigger a Simulation

The forked validator expose a nano web page to trigger a Simulation with modifiable parameters.

To open it, look at the URL in the terminal, but it should be: [localhost:8080](http://localhost:8080/)

> [!NOTE]
> Always look at the program's output for knowing what is happening within the system.
> The web page will not report successes or errors.
