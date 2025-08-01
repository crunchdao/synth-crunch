from datetime import datetime, timedelta

import numpy as np


# from https://github.com/mode-network/synth-subnet/blob/d076dc3bcdf93256a278dfec1cbe72b0c47612f6/synth/miner/price_simulation.py#L38
def simulate_single_price_path(
    current_price, time_increment, time_length, sigma
):
    """
    Simulate a single crypto asset price path.
    """
    one_hour = 3600
    dt = time_increment / one_hour
    num_steps = int(time_length / time_increment)
    std_dev = sigma * np.sqrt(dt)
    price_change_pcts = np.random.normal(0, std_dev, size=num_steps)
    cumulative_returns = np.cumprod(1 + price_change_pcts)
    cumulative_returns = np.insert(cumulative_returns, 0, 1.0)
    price_path = current_price * cumulative_returns
    return price_path


# from https://github.com/mode-network/synth-subnet/blob/d076dc3bcdf93256a278dfec1cbe72b0c47612f6/synth/miner/price_simulation.py#L55
def simulate_crypto_price_paths(
    current_price, time_increment, time_length, num_simulations, sigma
):
    """
    Simulate multiple crypto asset price paths.
    """

    price_paths = []
    for _ in range(num_simulations):
        price_path = simulate_single_price_path(
            current_price, time_increment, time_length, sigma
        )
        price_paths.append(price_path)

    return np.array(price_paths)


# from https://github.com/mode-network/synth-subnet/blob/d076dc3bcdf93256a278dfec1cbe72b0c47612f6/synth/utils/helpers.py#L11
def convert_prices_to_time_format(prices, start_time, time_increment):
    """
    Convert an array of float numbers (prices) into an array of dictionaries with 'time' and 'price'.

    :param prices: List of float numbers representing prices.
    :param start_time: ISO 8601 string representing the start time.
    :param time_increment: Time increment in seconds between consecutive prices.
    :return: List of dictionaries with 'time' and 'price' keys.
    """
    start_time = datetime.fromisoformat(
        start_time
    )  # Convert start_time to a datetime object
    result = []

    for price_item in prices:
        single_prediction = []
        for i, price in enumerate(price_item):
            time_point = start_time + timedelta(seconds=i * time_increment)
            single_prediction.append(
                {"time": time_point.isoformat(), "price": price}
            )
        result.append(single_prediction)

    return result
