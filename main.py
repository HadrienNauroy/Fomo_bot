"""A script to spot big pumps """

from binance.client import Client
from binance.enums import *
import config
import logging as lg
import json
import pprint as pp
import time as tm
from math import *
import os 
import itertools
import threading
import sys
from termcolor import colored
from message import *  


TIME_PERIOD = Client.KLINE_INTERVAL_1DAY
CEIL = 20 #the value over wich the bot will detect a raise in % 
SLEEP_TIME = 1800 #how long the program should wait before starting again
COLOR_CEIL = 50 #The value for colors


client = Client(config.API_KEY, config.API_SECRET, tld='com')
info = client.get_exchange_info()
browser = connect()

while True : 

	#only for display purpose
	done = False
	os.system("cls")
	print("%"*50)
	print(" "*15+ "Checking all pairs")
	print("%"*50)
	print("\n\n")


	#check all pairs
	for pair in info['symbols'] : 

		#select all BTC pairs
		if pair['symbol'][-3:] == 'BTC' :
			candle = client.get_historical_klines(pair['symbol'],TIME_PERIOD,"2 day ago")
			if candle != [] : 

				#checking variation an ping the user if necessary
				maxi = (float(candle[-1][4])/float(candle[-1][1]) - 1) * 100
				if maxi > CEIL : 
					
					#choose color for print 
					candle = client.get_historical_klines(pair['symbol'],Client.KLINE_INTERVAL_1DAY,"2 day ago")
					if (float(candle[-1][4])/float(candle[-1][1]) - 1) * 100 > COLOR_CEIL :
						color = "green"
					elif (float(candle[-1][4])/float(candle[-1][1]) - 1) * 100 < -COLOR_CEIL :
						color = "red"
					else : 
						color = "white"

					print(colored(pair['symbol'] + ": raise of " + str(floor(maxi*100)/100) + " %" +" in less than 1 day", color))
					send_message(browser, \
						pair['symbol'] + ": raise of " + str(floor(maxi*100)/100) + " %" +" in less than 1 day" \
						+ "\nhttps://www.binance.com/en/trade/"+pair['symbol'][:-3]+"_BTC")
					
					

	#wait and start again : 
	print("\n[Done] will restart in 30 minutes")
	tm.sleep(SLEEP_TIME)
		




