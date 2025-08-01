from abc import ABC, abstractmethod
from typing import Any, Literal

Asset = Literal["BTC", "ETH", "XAU", "SOL"]


class SynthMiner(ABC):

    # TODO: This prevent dynamic parameters... But we need some kind of pre/post processing to validate inputs and ensure outputs are serializable.
    def generate_simulations(
        self,
        asset: Asset,
        current_price: float,
        start_time: str = "",
        time_increment=300,
        time_length=86400,
        num_simulations=1,
        sigma=0.01,
    ):
        if start_time == "":
            raise ValueError("Start time must be provided.")

        result = self.do_generate_simulations(
            asset,
            current_price,
            start_time,
            time_increment,
            time_length,
            num_simulations,
            sigma,
        )

        # TODO: Convert to python list, could this step be skipped?
        return result

    @abstractmethod
    def do_generate_simulations(
        self,
        asset: Asset,
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
        pass
