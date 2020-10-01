import pandas as pd
import numpy as np
import GetAndProcessData as gd


# on reinstancie uniquement l'objet quand une erreur de connexion arrive
# et on relance

class Ichimoku(object):
	MEMORY_LENGTH = 78 
	TENKAN_SEN_PERIOD = 9
	KIJUN_SEN_PERIOD = 24
	CHIKOU_SPAN_DELAY = 26
	SENKOU_SPAN_A_PERIOD = 26
	SENKOU_SPAN_B_PERIOD = 52
	test = 0
	
	def __init__(self,gd_obj):
		#columns_candles = ['open_time', 'open','high', 'low', 'close', 'volume','close_time']
		self.gd_obj        = gd_obj
		self.df            = gd_obj.get_previous_values().iloc[:,0:5]
		self.tenkan_san    = Ichimoku._init_tenkan_sen(self.df)
		self.kijun_sen     = Ichimoku._init_kijun_sen(self.df)
		self.chikou_span   = Ichimoku._init_chikou_span(self.df)
		self.senkou_span_A = Ichimoku._init_senkou_span_A(self.df,self.tenkan_san,self.kijun_sen)
		self.senkou_span_B = Ichimoku._init_senkou_span_B(self.df)
		self.last_candle   = self.df.iloc[-1:]
		self.last_candle_1 = self.df.iloc[-2:-1]

		
	@classmethod
	def _min_max_avg(cls,df):
		'''
		Class mathod

		Parameters
		----------
		df : TYPE : Dataframe

		Returns float
		-------
			DESCRIPTION : mean of ichimoku

		'''

		maxi = df["high"].max()
		mini = df["low"].min()
		
		return (maxi + mini)/2

	@classmethod
	def _get_sub_df(cls,df,cursor,period): 
		'''
		Class mathod

		Parameters
		----------
		df : TYPE : Dataframe
		cursor : int
		period : int

		Returns dataframe
		-------
			DESCRIPTION : subdataframe from cursor to cursor + period

		'''
		nb_lines = df.shape[0]
		index_b,index_e = -(nb_lines - cursor), -(nb_lines - cursor) + period
		Ichimoku.test  +=1
		
		
		if index_e == 0:

			return df.iloc[index_b:]

		return df.iloc[index_b:index_e]
	
	@classmethod
	def _get_historical_values(cls,df,cursor,period):
		'''
		Class mathod

		Parameters
		----------
		df : TYPE : Dataframe
		cursor : int
		period : int

		Returns list
		-------
			DESCRIPTION : old values of Ichimoku means

		'''
		res = []
		for i in range(Ichimoku.SENKOU_SPAN_A_PERIOD):
			data = Ichimoku._get_sub_df(df,cursor,period)
			res.append(Ichimoku._min_max_avg(data))
			cursor +=1
			
		return res
	
	@classmethod
	def _init_tenkan_sen(cls,df):
		'''
		Class mathod 

		Parameters
		----------
		df : TYPE : Dataframe

		Returns list
		-------
			DESCRIPTION : list with the last 26 values of tenkan

		'''
		cursor = Ichimoku.MEMORY_LENGTH - Ichimoku.SENKOU_SPAN_A_PERIOD - Ichimoku.TENKAN_SEN_PERIOD + 1
		
		return  Ichimoku._get_historical_values(df,cursor,Ichimoku.TENKAN_SEN_PERIOD)
		
	@classmethod
	def _init_kijun_sen(cls,df):
		'''
		Class mathod

		Parameters
		----------
		df : TYPE : Dataframe

		Returns list
		-------
			DESCRIPTION : list with the last 26 values of kijun

		'''
		cursor = Ichimoku.MEMORY_LENGTH - Ichimoku.SENKOU_SPAN_A_PERIOD - Ichimoku.KIJUN_SEN_PERIOD + 1
		return Ichimoku._get_historical_values(df,cursor,Ichimoku.KIJUN_SEN_PERIOD) 
		
	
	@classmethod
	def _init_chikou_span(cls,df): 
		'''
		Class mathod

		Parameters
		----------
		df : TYPE : Dataframe

		Returns list
		-------
			DESCRIPTION : list with the last 26 values of closing prices(chikou_span)

		'''
		res = df.iloc[-Ichimoku.CHIKOU_SPAN_DELAY:]["close"].values.tolist()
		return res

	@classmethod
	def _init_senkou_span_A(cls,df,tekan,kijun):
		'''
		Class mathod

		Parameters
		----------
		df : TYPE : Dataframe
		tenkan : list with the last 26 tenkan values
		kijun : list with last 26 kijun values
		
	
		Returns list
		-------
			DESCRIPTION : list with the last 26 values of SSA

		'''
		res = []
		tool = list(zip(tekan, kijun))	
		for elem in tool:
			mean = (elem[0]+elem[1])/2
			res.append(mean)
		return res 
	
	@classmethod
	def _init_senkou_span_B(cls,df):
		'''
		Class mathod

		Parameters
		----------
		df : TYPE : Dataframe

		Returns list
		-------
			DESCRIPTION : list with the last 26 values of SSB

		'''
		cursor = Ichimoku.MEMORY_LENGTH - Ichimoku.SENKOU_SPAN_A_PERIOD - Ichimoku.SENKOU_SPAN_A_PERIOD + 1
		return Ichimoku._get_historical_values(df,cursor,Ichimoku.SENKOU_SPAN_A_PERIOD) 

	@classmethod 
	def _common_update(cls,df,period):
		'''
		Class method 
		
		update the value 

		'''
		data = df.iloc[-period:]

		return  Ichimoku._min_max_avg(data)
		 
	 
	def _update_tenkan_sen(self):
		'''
		
		update the value 

		'''
		new_mean = Ichimoku._common_update(self.df,Ichimoku.TENKAN_SEN_PERIOD)
		self.tenkan_san.append(new_mean)
		self.tenkan_san.pop(0)
		
	def _update_kijun_sen(self):
		'''
		
		update the value 

		'''
		new_mean = Ichimoku._common_update(self.df,Ichimoku.KIJUN_SEN_PERIOD)
		self.kijun_sen.append(new_mean)
		self.kijun_sen.pop(0)
		
	def _update_chikou_span(self):
		'''
		
		update the value 

		'''
		self.chikou_span.append(self.df["close"].iloc[-1])
		self.chikou_span.pop(0)
		
	def _update_senkou_span_A(self):
		'''
		
		update the value 

		'''
		new_mean = (self.tenkan_san[-1] + self.kijun_sen[-1])/2
		self.senkou_span_A.append(new_mean)
		self.senkou_span_A.pop(0)
		
	def _update_senkou_span_B(self):
		'''
		
		update the value 

		'''
		new_mean = Ichimoku._common_update(self.df,Ichimoku.SENKOU_SPAN_B_PERIOD)
		self.senkou_span_B.append(new_mean)
		self.senkou_span_B.pop(0)
	
	def _update_last_candle(self):
		'''
		
		update the value 

		'''
		self.last_candle   = self.df.iloc[-1:]


	def update(self):
		'''
		
		update the values 

		'''
		self.last_candle_1 = self.last_candle
		self.df = self.df.append(self.gd_obj.get_recent_data(), ignore_index=True)
		self.df = self.df.iloc[:,0:5]
		Ichimoku._update_last_candle(self)
		Ichimoku._update_tenkan_sen(self)
		Ichimoku._update_kijun_sen(self)
		Ichimoku._update_chikou_span(self)
		Ichimoku._update_senkou_span_A(self)
		Ichimoku._update_senkou_span_B(self)
		self.df = self.df.drop(self.df.index[0])
		
