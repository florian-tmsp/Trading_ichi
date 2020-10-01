# -*- coding: utf-8 -*-

from binance.client import Client
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta


class GetAndProcessData(object):

	columns_candles = ['open_time', 'open','high', 'low', 'close', 'volume','close_time']
	LONGUEST_PERIOD = 78
	
	def __init__(self,key1 ,key2 ,product):
		'''
		

		Parameters
		----------
		key1 : TYPE : string
			DESCRIPTION first key of user
		key2 : TYPE
			DESCRIPTION.
		product : TYPE string
			DESCRIPTION second key of user
		b_time : TYPE sting
			DESCRIPTION 3 months before the moment with shape day month, year

		Returns
		-------
		None.

		'''
		self.client   = Client(key1,key2)
		self.interval = self.client.KLINE_INTERVAL_1DAY
		self.product  = product 
		self.b_time   = GetAndProcessData._init_b_time()
	
	def get_server_time(self):

		'''
		Sends a request to the server

		Returns int
		-------
		TYPE
			DESCRIPTION : server_time

		'''
		return self.client.get_server_time()['serverTime']

	def get_previous_values(self): #appelle get_kline_historical 
	
		'''
		Send a request to the server

		Returns pandas dataframe 
		-------
		TYPE
			DESCRIPTION :  dataframe containing 7 columns describing the last 78 periods
			
			columns =  ['open_time', 'open','high', 'low', 'close', 'volume','close_time']

		'''
		klines = self.client.get_historical_klines(self.product, self.interval,self.b_time )
		df = GetAndProcessData._clean_data(klines)
		df = df[-GetAndProcessData.LONGUEST_PERIOD:]
		return df
	
	def get_recent_data(self):
		'''
		
		Send a request to the server
		
		Returns pandas series
		-------
		TYPE
			DESCRIPTION :  last information given by the API depending on the period

		'''
		recent_data = self.client.get_klines(symbol  = self.product,interval = self.interval,limit = 10)
		return GetAndProcessData._clean_data(recent_data).iloc[-1]
	
	@classmethod
	def _process_types(cls,df):
		'''
		Class method

		Parameters
		----------
		
		df : TYPE : pandas dataframe
			DESCRIPTION : dataframe containing 7 columns
			columns =  ['open_time', 'open','high', 'low', 'close', 'volume','close_time']

		Returns
		-------
		df : Dataframe
			DESCRIPTION : dataframe with casted types

		'''
		columns_candles_float = ['open','high', 'low', 'close', 'volume']
		for elem in columns_candles_float:
			df[elem] = pd.to_numeric(df[elem], downcast="float")
		
		#manage time format 
		df['open_time']=pd.to_datetime(df['open_time'], unit='ms')
		df['close_time']=pd.to_datetime(df['close_time'], unit='ms')
		
		return df
	
	@classmethod	
	def _clean_data(cls,api_responce): 
		'''
		Class method

		Parameters
		----------
		
		df : TYPE : pandas dataframe
			DESCRIPTION : response of the server
			

		Returns
		-------
		df : Dataframe
			DESCRIPTION : dataframe cleaned with date processed and columns renamed and dropped
			
		'''
		
		df = pd.DataFrame(api_responce)
		df = df.iloc[:,:7]
		df.columns = GetAndProcessData.columns_candles 
		df = GetAndProcessData._process_types(df)
		return df


	def get_avg_price(self):
		'''

		Returns tuple : (avg_price,min_quant)
		-------
		avg_price : float
			DESCRIPTION : average price of the product 
		min_quant : int
			DESCRIPTION : minimum quantity to be bought to validate the trade

		'''

		
		avg_price = float(self.client.get_avg_price(symbol=self.product)['price'])
		min_quant = int(self.client.get_avg_price(symbol=self.product)['mins'])
		return avg_price,min_quant

	def get_balance(self):
		'''
		

		Returns balance
		-------
		balance : int
			DESCRIPTION the amount of credit in the account

		'''
		if self.client.get_asset_balance(self.product) == None:
			return 0
		return float(self.client.get_asset_balance(self.product)['free'])

	@classmethod
	def _init_b_time(cls):
		date_init = date.today() + relativedelta(months=-4)
		date_init = date_init.strftime('%m/%d/%Y')
		inv_dico_index = {0 : 'Jan',1: 'Feb',2: 'Mar',3: 'Apr',4: 'May',5: 'Jun',6: 'Jul',7: 'Aug',8: 'Sep',9: 'Oct',
						 10: 'Nov',11: 'Dec'}
		month = int(date_init[:2])
		month = inv_dico_index[month-1]
		day = str(int(date_init[3:5]))
		year = str(date_init[6:])
		res = day +' '+ month + ', ' +  year
		
		return res
		
		
		
		
		
		
		
		
		
		
		