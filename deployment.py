# -*- coding: utf-8 -*-
import time 
import GetAndProcessData
import Ichimoku
import Order
from time import ctime


def main(ichi,period,gd):
	ichi.update()
	order_obj = Order.Order(ichi,gd)
	order_obj.signal_achat()
	order_obj.signal_vente()
	time.sleep(period)
	main(ichi,period,gd)

	
if __name__ == "__main__":
	I1 = input("Give the first binance key:")
	I2 = input("Give the second binance key:")
	I3 = input("Give the product name:")
	gd = GetAndProcessData.GetAndProcessData(key1 =I1,key2 =I2,product =I3)
	ichi = Ichimoku.Ichimoku(gd)
	period = 86401
	var = str(ctime())[-13:-5]
	hours   = int(var[:2])
	minutes = int(var[3:5])
	seconds = int(var[6:])
	init = 86401 - hours*3600 - minutes*60 - seconds
	time.sleep(init)
	main(ichi,period,gd)
# Automatisation du processus via Cron
