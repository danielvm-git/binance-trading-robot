## Crypto trading bot

### Introduction
This is a crypto trading bot, I have done. Which receives webhooks from `Tradingview`.
When to enter and exit both longs and short position. The indicator I use, is from
[Bobby B](https://www.youtube.com/channel/UCs6gG84TWU2M4YqzdjoM0tQ).

### Logic behind the Trading Bot
The trading bot will receive a webhook from TV, with a few parameters, which you can find in the folder `Webhook`. 
You need to add this message to your TV indicator signal, and tick off the `webhook` field. In the input box, 
add your URL/webhook.

The bot will make a calculation of the `portion size` based on your account balande and stop limit (which is sent from TV).
Everytime the bot makes a trade, it will append in a `running_trades.json`, and update the values accordingly.
For example the current P/L will be updated as soon as you refresh your web browser.
When the bot gets an `exit signal`. It will loop through all the `running_trades.json`, and filter through the trades.
It will find the previous trade, it made, based on the correct coinpair and interval.
Hence, you can have multiply trades from the same coinpair, with different intervals.

FIY, if you have a lot of signals, sending webhooks as the same time (you have many coinpairs at the same interval).
You might consider scaling up your server, depending on your CPU.

At this moment the bot can only trade on your `cross margin account`. If you don't have enought funds, it will borrow 
the remaining funds to be able to do the trade. From cross margin, you can borrow up to 3x of your account balance.
This project is still in development, and I will commit new changes weekly.

### Dashboard
The dashboard will show your `running_trades.json` and `all_trades.json` (exit trades). As soon as the bot exit
a trade from the running_trades, it will delete the column from running_trades and append it to the exit trades, below.

### Risk
I have implemeted a risk factor of 1%, which means you can only lose up to 1% of your balance per trade. You may adjust
the risk_factor in `calculate.py` accordingly, due to own preferences.

### For your own safetly
When you launch your bot, please monitor your bot manually on a daily basis. If an error occurs, and the bot can't exit a trade. 
I don't want to be responsible if you loose any $$$ in the process.

### How to set up a server
This video is great to learn how to deploy your application to a server.
[How to deploy an app to your server](https://www.youtube.com/watch?v=goToXTC96Co).
Follow this video.


### Setup

Install Git

`pip install git`

Install python3

`pip install python3`

Change directory to your project

`cd "your_project" folder`

Install virtuel environment

`pip install python3-venv`

Clone my repo

`git clone https://github.com/amfchef/binance-trading-bot.git`

Create a virtuel environment

`virtualenv venv` 

Activate virtuel environment

`source venv/bin/activate`

Install dependencies

`pip install -r requirements.txt`


### Create your Binance API
[Binance API management](https://www.binance.com/en/my/settings/api-management)

You will receive an API-key and API-secret number. You need to add these numbers to the `setup.py` file.

