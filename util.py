# In a Jupyter Notebook cell
from datetime import datetime, timedelta
import pandas as pd
import datetime as dt
import requests as rq
from NorenRestApiPy.NorenApi import NorenApi
from pyotp import TOTP
import json
import calendar
from telegram import Bot
from telegram.ext import Updater, CommandHandler, CallbackContext ,JobQueue
import logging
from queue import Queue
import requests
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
import time
import zipfile
import os

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                        websocket='wss://api.shoonya.com/NorenWSTP/')

class ShoonyaHelper:
    def __init__(self):
        pass

    def login_shoonya(self): 
        api = ShoonyaApiPy()
        with open(f"cred.json", "r") as f:
            Cread = json.load(f)
        user = Cread['user_id']
        pwd = Cread['password']
        factor2 = Cread['totp']
        vc = Cread['vendor_code']
        app_key = Cread['api_key']
        imei = Cread['imei']
        otp = TOTP(factor2).now().zfill(6)
        ret = api.login(userid=user, password=pwd, twoFA=otp,vendor_code=vc, api_secret=app_key, imei=imei)
        return ret, api 

    def get_last_thursday(self, year, month):
        # Get the last day of the given month
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        # Calculate the difference to find the weekday of the last day
        diff = (last_day.weekday() - 3) % 7
        # Calculate the last Thursday
        last_thursday = last_day - timedelta(days=diff)
        
        return last_thursday

    def send_notification_telegram(self, message):
        bot_token = '********'
        channel_id = '*********'
        # Initialize the bot
        bot = Bot(token=bot_token)
        # Send the message to the specified channel
        try:
            bot.send_message(chat_id=channel_id, text=message)
            time.sleep(4) 
            print("Message sent successfully!")
        except Exception as e:
            print(f"Failed to send message. Error: {str(e)}")

    def download_token_files(self, *args, **kwargs):
        root = 'https://api.shoonya.com/'

        for zip_file in args:
            print(f'downloading {zip_file}')
            url = root + zip_file
            r = requests.get(url, allow_redirects=True)
            open(zip_file, 'wb').write(r.content)
            file_to_extract = zip_file.split()
        
            try:
                with zipfile.ZipFile(zip_file) as z:
                    z.extractall()
                    print("Extracted: ", zip_file)
            except:
                print("Invalid file")

            os.remove(zip_file)
            print(f'remove: {zip_file}')

