%run date_utility.py
%run util.ipynb
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
import json


masters = ['NSE_symbols.txt.zip', 'NFO_symbols.txt.zip']
stk_nfo_bnf_last_thrusday_month_tokens = []
stk_nfo_bnf_next_month_token = []
stk_nse_token = []

data_nsc = []

shoonya_helper = ShoonyaHelper()
ret, api = shoonya_helper.login_shoonya()

with open(f"NFO_symbols.txt", "r") as f:
         data = f.read()
lines = data.strip().split('\n')         


# Get current date
current_date = datetime.now()
# Current month
current_month_last_thursday = shoonya_helper.get_last_thursday(current_date.year, current_date.month)
# Next month
next_month_last_thursday = shoonya_helper.get_last_thursday(current_date.year, current_date.month + 1)
# Next to next month
next_to_next_month_last_thursday = shoonya_helper.get_last_thursday(current_date.year, current_date.month + 2)

current_month = current_month_last_thursday.strftime('%d-%b-%Y').upper()
next_month = next_month_last_thursday.strftime('%d-%b-%Y').upper()
next_next_month = next_to_next_month_last_thursday.strftime('%d-%b-%Y').upper()

# print(current_month,next_month,next_next_month)
current_date = current_date.strftime('%d-%b-%Y').upper()
# print(current_date,currnt_exp,next_month)
crnt_date = datetime.strptime(current_date, '%d-%b-%Y')
crnt_month = datetime.strptime(current_month, '%d-%b-%Y')

# print(crnt_date,crnt_month)

    # Compare dates
if crnt_date > crnt_month:
    shoonya_helper.download_token_files(*masters)
    # Print lines that contain "OPTSTK" in the "Instrument" column
    for line in lines:
        if "FUTIDX" in line and next_month in line and "BANKNIFTY" in line :
            columns = line.split(',')
            # print(columns)
            token_number = columns[1].strip()
            stk_nfo_bnf_last_thrusday_month_tokens.append(token_number)

    for line in lines:
        if "FUTIDX" in line and next_next_month in line and "BANKNIFTY" in line :
            columns = line.split(',')
            # print(columns)
            token_number = columns[1].strip()
            stk_nfo_bnf_last_thrusday_month_tokens.append(token_number)
else:
    # Print lines that contain "OPTSTK" in the "Instrument" column
    for line in lines:
        if "FUTIDX" in line and current_month in line and "BANKNIFTY" in line :
            columns = line.split(',')
            # print(columns)
            token_number = columns[1].strip()
            stk_nfo_bnf_last_thrusday_month_tokens.append(token_number)

    for line in lines:
        if "FUTIDX" in line and next_month in line and "BANKNIFTY" in line :
            columns = line.split(',')
            # print(columns)
            token_number = columns[1].strip()
            stk_nfo_bnf_last_thrusday_month_tokens.append(token_number)

stk_nfo_bnf_last_thrusday_month_tokens

exch  = 'NSE'
nsc_bnf_token = ['26009'] # this remain same whole year


nfo_exch = 'NFO'
nfo_token = stk_nfo_bnf_last_thrusday_month_tokens

# print(stk_nfo_bnf_last_thrusday_month_tokens)


for i  in nsc_bnf_token:
     ret = api.get_quotes(exchange=exch,token=str(i))
     data_nsc.append(ret['lp'])

for i  in stk_nfo_bnf_last_thrusday_month_tokens:
     ret_nfo = api.get_quotes(exchange=nfo_exch,token=str(i))
     data_nsc.append(ret_nfo['lp'])


# Initialize an empty list to store the results
results = []

# Perform subtraction and save results to a new variable
for i in range(len(data_nsc) - 1):
    result = float(data_nsc[i]) - float(data_nsc[i + 1])
    results.append(result)

current_to_next_fut_diff = round(results[-1],2)
sport_to_current_diff = round(results[0],2)
if 90 < current_to_next_fut_diff <= 120:
        message = f"Alert: Current to next fut diff : {current_to_next_fut_diff} and spot to current fut {sport_to_current_diff}"
        shoonya_helper.send_notification_telegram(message)

print(results)
