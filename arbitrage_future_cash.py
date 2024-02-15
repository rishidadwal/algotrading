%run util.ipynb
import pandas as pd
import datetime as dt
import requests as rq
from NorenRestApiPy.NorenApi import NorenApi
from pyotp import TOTP
import json
import calendar
from datetime import datetime, timedelta
from telegram import Bot
from telegram.ext import Updater, CommandHandler, CallbackContext ,JobQueue
import logging
from queue import Queue
import requests
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
import time
# from shoonya_helper import ShoonyaHelper


shoonya_helper = ShoonyaHelper()
ret, api = shoonya_helper.login_shoonya()

stk_nfo_token = []
nsc_name = []
stk_nse_token = []
nse_stk_name = []
data_nsc = {}
data_fno = {}
masters = ['NSE_symbols.txt.zip', 'NFO_symbols.txt.zip']

with open(f"NFO_symbols.txt", "r") as f:
         data = f.read()

lines = data.strip().split('\n')


def last_thursday_of_month(year, month):
    # Find the last day of the month
    last_day = calendar.monthrange(year, month)[1]

    # Get the date of the last day of the month
    last_day_date = datetime(year, month, last_day)

    # Find the weekday of the last day (Monday is 0 and Sunday is 6)
    last_day_weekday = last_day_date.weekday()

    # Calculate the number of days to subtract to get to the last Thursday
    days_to_subtract = (last_day_weekday - 3 + 7) % 7

    # Calculate the date of the last Thursday
    last_thursday = last_day_date - timedelta(days=days_to_subtract)

    return last_thursday


# Example usage
current_year = datetime.now().year
current_month = datetime.now().month
last_thursday = last_thursday_of_month(current_year, current_month)
# print("Last Thursday of the month:", last_thursday.strftime('%d-%b-%Y').upper())

currnt_exp = last_thursday.strftime('%d-%b-%Y').upper()
currnt_exp
date = datetime.now()

next_month = (date.month % 12) + 1  # Calculate the next month, considering December
next_month_last_thursday = last_thursday_of_month(date.year + (date.month // 12), next_month)
# print(f"Last Thursday of the next month: {next_month_last_thursday.strftime('%d-%b-%Y').upper()}")
next_month = next_month_last_thursday.strftime('%d-%b-%Y').upper()

current_date = date.strftime('%d-%b-%Y').upper()
# print(current_date,currnt_exp,next_month)

current_date = datetime.strptime(current_date, '%d-%b-%Y')
currnt_exp = datetime.strptime(currnt_exp, '%d-%b-%Y')
next_month = datetime.strptime(next_month, '%d-%b-%Y')
nxt_month = next_month.strftime('%d-%b-%Y').upper()
this_month_exp = currnt_exp.strftime('%d-%b-%Y').upper()
this_crnt_exp = currnt_exp.strftime('%d-%b-%Y').upper()

# print(next_month,nxt_month,currnt_exp,this_month_exp)


# Compare the dates
if current_date >= currnt_exp:   # 21-FEB-2024 >= 29-FEB-2024
    shoonya_helper.download_token_files(*masters)
    for line in lines:
        if "FUTSTK" in line and nxt_month in line:
            columns = line.split(',')
            #    print(columns)
            token_number = columns[1].strip()
            stk_nfo_token.append(token_number)
            nsc_stock_name = columns[3].strip()
            nse_stk_name.append(nsc_stock_name)
else:
    for line in lines:
        if "FUTSTK" in line and this_crnt_exp in line:
            columns = line.split(',')
            #    print(columns)
            token_number = columns[1].strip()
            stk_nfo_token.append(token_number)
            nsc_stock_name = columns[3].strip()
            nse_stk_name.append(nsc_stock_name)
    
for i in nse_stk_name:
     stk_name= api.searchscrip(exchange='NSE', searchtext=i)
     stk_nse_token.append(stk_name['values'][0]['token'])

exch  = 'NSE'
# token = ['7','13']
nsc_token = stk_nse_token

nfo_exch = 'NFO'
# nfo_token = ['55319','55320']
nfo_token = stk_nfo_token


for i  in nsc_token:
     ret = api.get_quotes(exchange=exch,token=str(i))
     data_nsc[ret['symname']] = ret['lp']

     
for i  in nfo_token:
     ret_nfo = api.get_quotes(exchange=nfo_exch,token=str(i))
     data_fno[ret_nfo['symname']] = ret_nfo['lp']


common_keys = set(data_nsc.keys()) & set(data_fno.keys())

for key in common_keys:
    nsc_value = float(data_nsc[key])
    nfo_value = float(data_fno[key])
#     print(nsc_value)
#     print(nf0_value)

    if nsc_value and nfo_value:
        # Calculate percentage difference
        percentage_diff = ((nfo_value - nsc_value) / nsc_value) * 100
        if percentage_diff < 0 :
             print(f"skip negative number{percentage_diff:.2f}% ")
        else:
        # Check if the absolute value of the percentage difference is greater than 2
          if abs(percentage_diff) > 1.5:
            # Send alert to Telegram
            message = f"Alert: Percentage difference for {key} is {percentage_diff:.2f}%"
            shoonya_helper.send_notification_telegram(message)
