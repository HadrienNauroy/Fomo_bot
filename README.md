# Fomo_bot
A bot based on binance that has fomo. 
 
### /!\ This bot is only for educational purpose, trade with it at your own risk /!\

## Requirements

- [Python](https://www.python.org/)
- [Binance account](https://accounts.binance.com/en/login) 
- [Selenium](https://selenium-python.readthedocs.io/) (optional)

## How to use the bot 

- Create a binance account and set your API keys in the config.py file.
- run the following comand 
```sh
py trade.py
```

## Description

The bot is based on the size of the candles and act roughly as follows :
- Compute the mean size of candles
- If a candle is anormaly big buy
- Sell at fixed TP or Stop loss

