"""
A script to spot big pumps and surf them !

The time period can be choosen (we test with 15mins)
The bot is based on the size of the candles and act as follows :
    - Compute the mean size of candles
    - If a candle is anormaly big buy
    - Sell if price go down again or at fixed TP 
"""
import logging as lg
from binance.client import Client
from binance.enums import *
import config
import time as tm
import os
import statistics
from termcolor import colored
from message import *
from math import *
import json
from objects import Data

# Settings variables
TEST_MODE = True  #                             not trading real money
QUICK_MODE = False  #                           avoid some initial calculation
TIME_PERIOD = Client.KLINE_INTERVAL_15MINUTE  # interval for data
DETECTION_RATIO = 5  #                         detection ratio for pump
DETECTION_FLOOR = 0.03  #                        detection floor  for pump
BTC_AMOUNT = 0.0004  #                          amount available for trading
STOP = 0.95  #                                  initial stop loss
ABSOLUT_STOP = 0.95  #                          maximum loss allowed
MARGIN_TIME = 30  #                             complex stop loss time
TAKE_PROFIT = 1.01  #                           Take Profit
WAIT_TIME = 180  #                              Time we let the bot doing nothing


# only for display pupose :
SPACE = "               "


def main():

    # for Binance API
    client = Client(config.API_KEY, config.API_SECRET, tld="com")
    # for sending message to user
    # browser = connect()

    # only for display purpose
    share_info()

    # set up

    if QUICK_MODE:
        with open("save.json", "r") as file:
            means = json.load(file)
            pairs = list(means.keys())
    else:
        pairs = get_BTC_pairs(client)
        means = get_means(client, pairs)
        pairs = list(means.keys())  # avoid young pairs

    # saving means (for QUICK MODE)
    with open("save.json", "w") as file:
        json.dump(means, file)

    # trade
    total_changes = 0
    data = Data(client, pairs, means)
    while True:
        # pair = select_pair(client, data)
        pair, data = combined_select_pair(pairs, data)
        if pair != None:
            changes, data = trade(pair, data)
            total_changes += changes - 0.0015
            print(f"-> {round(total_changes,2)}% changes since the begining\n")
        else:
            print(f"Nothing intresting just waiting\r", end="")
            # tm.sleep(60)
        tm.sleep(0.5)


def share_info():
    """Only for display purpose"""

    os.system("cls")
    print("%" * 50)
    print(" " * 20 + "Now live ! ")
    print("%" * 50)
    print("\n\n")
    print(
        f"Stop: {STOP}, Absolut stop: {ABSOLUT_STOP}, Margin time: {MARGIN_TIME}, Take profit: {TAKE_PROFIT}"
    )

    print(
        f"Waiting time: {WAIT_TIME}, Detection ratio: {DETECTION_RATIO}, Detection floor: {DETECTION_FLOOR} \n"
    )


def get_BTC_pairs(client):
    """This function is aimed to retrieve all BTC pairs from binance"""

    res = []

    # check all pairs
    info = client.get_exchange_info()
    for pair in info["symbols"]:

        # select all BTC pairs
        if pair["symbol"][-3:] == "BTC":
            res += [pair["symbol"]]

    return res


def get_means(client, pairs):
    """This function is aimed to get the mean size of candles for all pairs"""

    # only for display purpose :
    print("Computing means: [Working]")

    means = {}

    # go through all pairs
    for pair in pairs:
        candles = client.get_historical_klines(pair, TIME_PERIOD, "2 day ago")
        if len(candles) > 150:  # here we avoid young pairs !
            sizes = [
                abs(float(candle[3]) - float(candle[2])) for candle in candles
            ]  # note that this is the size with mesh !
            means[pair] = statistics.mean(sizes)

    # only for display purpose :
    print("Computing means: [Done]\n")

    return means


def select_pair(client, data):
    """
    This function is aimed to select the best pair to trade on
    which means the one with the highest size ratio
    This ratio also has to be greater than 1
    """

    res = None
    max_ratio = 1

    # check all pairs
    for pair in data.btc_pairs:

        candle = client.get_historical_klines(pair, TIME_PERIOD, "1 hour ago")[-1]
        size = float(candle[4]) - float(
            candle[1]
        )  # note that there is no abs() here, and that this is the size without mesh !
        ratio = size / (DETECTION_RATIO * data.means[pair])
        price = float(candle[4])

        if (
            (pair in data.traded.keys()) and (price > data.traded[pair])
        ) or not pair in data.traded.keys():  # to be sure not to rebuy something to low

            if ratio > max_ratio:  # note that ratio has to be positive !
                res = pair
                max_ratio = ratio

    return res


def fast_select_pair(pairs, data):
    """
    This function is aimed to select the best pair to trade on
    which means the one with the highest increse during the last 15 minutes
    """

    res = None
    data.update()
    old_price = data.prices[0][pairs[0]]
    actual_price = data.current_prices[pairs[0]]
    max_increase = (actual_price - old_price) / old_price  # within 15mins

    # go trough all pairs
    for pair in pairs:

        # to be sure not to rebuy something going down
        if (
            (pair in data.traded.keys())
            and (data.current_prices[pair] > data.traded[pair])
        ) or not pair in data.traded.keys():  # to be sure not to rebuy something going down

            old_price = data.prices[0][pair]
            actual_price = data.current_prices[pair]
            increase = (actual_price - old_price) / old_price  # within 15mins

            # checking if the price is going wild !
            if increase >= DETECTION_FLOOR and increase > max_increase:
                res = pair
                max_increase = increase
    return res, data


def combined_select_pair(pairs, data):
    """
    This function is aimed to select the best pair to trade on
    by combining the two previous methods
    """

    res = None
    data.update()
    old_price = data.prices[0][pairs[0]]
    actual_price = data.current_prices[pairs[0]]
    max_increase = (actual_price - old_price) / old_price  # within 15mins

    # go trough all pairs
    for pair in pairs:

        # to be sure not to rebuy something going down
        if not pair in data.traded.keys():
            # or
            # (
            #     pair in data.traded.keys()
            #     and data.current_prices[pair] > data.traded[pair]
            #     and data.nb_trades[pair] > 2
            #     and data.last_trades[pair][-1] > 0
            # )
            # or (
            #    pair in data.traded.keys()
            #     and data.current_prices[pair] > data.traded[pair]
            #     and data.nb_trades[pair] < 2
            # )

            # to be sure not to rebuy something going down

            # for computation
            old_price = data.prices[0][pair]
            actual_price = data.current_prices[pair]
            variation = actual_price - old_price
            increase = variation / old_price  # within 15mins

            # checking if the price is going wild !
            if (
                increase >= DETECTION_FLOOR
                and increase > max_increase
                and variation > DETECTION_RATIO * data.means[pair]
            ):
                res = pair
                max_increase = increase

    return res, data


def trade(pair, data):
    """
    This function is aimed to manage trades.
    The following strategie is implemented :
        1) Buy the previously selected pair
        2) Set stop loss to STOP_LOSS * buy_price
        3) Set take profit to TAKE_PROFIT * buy_price
        4) While price goes up set stop loss to STOP_LOSS * price
        5) Sell when stop loss or take profit is reached is reached
        6) Si rien ne se passe vend au bout de WAIT_TIME
    """

    # initialisze
    tradable = True
    data.update()
    # price = float(client.get_historical_klines(pair, TIME_PERIOD, "2 hour ago")[-1][4])
    price = data.current_prices[pair]
    quantity = get_quantity(data.client, pair, price)
    buy_price = price
    stop_loss = price * STOP
    max_price = price
    take_profit = price * TAKE_PROFIT
    toc = tm.time()
    tic = tm.time()

    # buy
    make_order(data.client, SIDE_BUY, pair, quantity)
    print(
        f"Buying {pair} at {price} [{tm.localtime().tm_hour}h{tm.localtime().tm_min}]{SPACE}"
    )

    # update every seconds (or less)
    while tradable:

        data.update()
        price = data.current_prices[pair]
        tic = tm.time()

        print(
            f"Stop loss set at {round(stop_loss,10)}, Current price: {price}{SPACE}\r",
            end="",
        )

        # selling case (stop loss)
        if price <= stop_loss:
            tradable, sell_price, data = time_stop_loss(pair, max_price, quantity, data)
            if not tradable:
                changes = round((sell_price / buy_price - 1) * 100, 2)  # changes in %
                print(
                    f"Selling at {sell_price}, {changes}% changes since buy order {SPACE}"
                )
            else:
                toc = tm.time()  # finaly we haven't sell

        # update stop loss case
        elif price > max_price:
            stop_loss = price * STOP
            max_price = price
            toc = tm.time()

        # selling case (take profit)
        if price >= take_profit:
            tradable, sell_price, max_price, data = smart_TP(
                pair, buy_price, quantity, data
            )
            # make_order(data.client, SIDE_SELL, pair, quantity)
            changes = round((sell_price / buy_price - 1) * 100, 2)  # changes in %
            print(
                f"Selling at {sell_price}, {changes}% changes since buy order {SPACE}"
            )

        # selling case (too much time)s

        if tic - toc > WAIT_TIME:
            tradable = False
            make_order(data.client, SIDE_SELL, pair, quantity)
            changes = round((price / buy_price - 1) * 100, 2)
            print(f"Selling at {price}, {changes}% changes since buy order {SPACE}")

        # nothing to do case
        else:
            pass

        tm.sleep(0.2)  # we would prefer 0.1 but connection is to slow here

    # adding current trading pair to traded pair to avoid miss trading it after
    data.update_trade(pair, max_price, changes)
    return changes, data


def time_stop_loss(pair, max_price, quantity, data):
    """
    This function is aimed to sell inteligently it will act as follow :
        - if price remain under stop loss sell
        - if price goes slightly higer sell at better cost
        - if price drops to much sell
        - if price keep going up cancel stop loss

    It is very dependant of MARGIN_TIME
    """

    stop_loss = STOP * max_price
    toc = tm.time()
    tic = tm.time()
    while tic - toc < MARGIN_TIME:

        data.update()
        price = data.current_prices[pair]
        print(
            f"Stop loss set at {round(stop_loss,10)}, Current price: {price}{SPACE}\r",
            end="",
        )

        # break up case
        if price > max_price:
            return True, None, data  # no changes here as order has been canceled

        # break down case
        if price < max_price * ABSOLUT_STOP:
            make_order(data.client, SIDE_SELL, pair, quantity)
            return False, price, data

        tm.sleep(0.2)  # we would prefer 0.1 but connection is to slow here
        tic = tm.time()

    # time passed case
    make_order(data.client, SIDE_SELL, pair, quantity)
    return False, price, data


def smart_TP(pair, max_price, quantity, data):
    """
    This function is a smart take profit ie: don't sell if it keeps going up
    It act as follow :
        - if price < TP sell
        - if price goes up TP goes up
    """

    take_profit = max_price
    last_price = data.current_prices[pair]

    while True:

        data.update()
        price = data.current_prices[pair]

        # selling case (going down)
        if price < take_profit:
            make_order(data.client, SIDE_SELL, pair, quantity)
            return False, price, take_profit, data

        # update TP case
        elif price > last_price:
            take_profit = last_price

        last_price = price
        tm.sleep(0.1)


def get_quantity(client, pair, price):
    """This function is aimed to get a correct quantity"""

    info = client.get_symbol_info(pair)
    lot_size_filter = info["filters"][2]
    min_qty = float(lot_size_filter["minQty"])
    step_size = float(lot_size_filter["stepSize"])
    raw_quantity = BTC_AMOUNT / price
    quantity = min_qty + ((raw_quantity - min_qty) // step_size) * step_size
    return round(quantity, 10)  # to avoid python float error


def make_order(client, side, pair, quantity):

    if TEST_MODE:
        client.create_test_order(
            symbol=pair,
            side=side,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity,
        )

    else:
        client.create_order(
            symbol=pair,
            side=side,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity,
        )


if __name__ == "__main__":
    main()
