"""A script that define useful classes for our main script"""

import time as tm


class Data:

    """
    This class is a local set of 15 min candle divided in five 3 minutes candles
        -data.prices[0] is the price ~15min ago for each btc pair
        -data.prices[-1] is the latest close price for each btc pair
        -timstanp is the time of last update
        -current_prices is the actual price
        -tradded is a dict of already traded pairs is their previous price
        -means is the mean size of candles (with mesh) for each btc pair
        -last_trade is a history of previous changes fo a given pair
        -nb_trade is the number of trade for each pair
        -last_trade_time is the time of the last trade for each pair
    """

    def __init__(self, client, btc_pairs, means):

        print(f"Initialising data [{tm.localtime().tm_hour}h{tm.localtime().tm_min}]")
        self.client = client
        self.timestamp = tm.time()
        self.btc_pairs = btc_pairs
        self.traded = {}
        self.means = means
        self.last_trade = {}
        self.nb_trades = {}
        self.last_trade_time = {}

        tickers = self.client.get_all_tickers()
        tickers_dict = {
            tickers[k]["symbol"]: tickers[k]["price"] for k in range(len(tickers))
        }
        self.prices = [{pair: float(tickers_dict[pair]) for pair in self.btc_pairs}]

        for _ in range(4):
            tm.sleep(1)  # /!\ only for test 180 else
            tickers = self.client.get_all_tickers()
            tickers_dict = {
                tickers[k]["symbol"]: tickers[k]["price"] for k in range(len(tickers))
            }
            self.prices += [
                {pair: float(tickers_dict[pair]) for pair in self.btc_pairs}
            ]
            self.timestanp = tm.time()

        self.current_prices = self.prices[-1]
        print("Initialising data [Done]\n")

    def update(self):
        """ "A function aimed to update market data"""

        # update current price
        tickers = self.client.get_all_tickers()
        tickers_dict = {
            tickers[k]["symbol"]: tickers[k]["price"] for k in range(len(tickers))
        }

        self.current_prices = {
            pair: float(tickers_dict[pair]) for pair in self.btc_pairs
        }

        # update candle
        if tm.time() - self.timestamp > 180:
            self.prices = self.prices[1:] + [self.current_prices]
            self.timestamp = tm.time()

    def update_trade(self, pair, max_price, changes):
        """A function update data about traded pairs after each trade"""

        self.traded[pair] = max_price
        self.last_trade_time[pair] = tm.time()

        # already traded
        try:
            self.last_trade[pair] += [changes]
            self.nb_trades[pair] += 1

        # not already traded
        except KeyError:
            self.last_trade[pair] = [changes]
            self.nb_trades[pair] = 1
