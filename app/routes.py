from app import app
from app import config
from app import exchange
from app import database
from app import controller
from app import preparation
from app import asynco
import sys
import logging
from flask import request, jsonify, json

# * ###########################################################################
# * LOGGING INSTANTIATION RETURNING ON CONSOLE
# * ###########################################################################
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# * ###########################################################################
# * CONFIG CLASS INSTANTIATION
# * ###########################################################################
config_client = config.ConfigClient()

# * ###########################################################################
# * EXCHANGE CLASS INSTANTIATION
# * ###########################################################################
exchange_client = exchange.ExchangeClient()

# * ###########################################################################
# * DATABASE CLASS INSTANTIATION
# * ###########################################################################
database_client = database.DatabaseClient()

# * ###########################################################################
# * CONTROLLER CLASS INSTANTIATION
# * ###########################################################################
controller_client = controller.ControllerClient()

# * ###########################################################################
# * PREPARATION CLASS INSTANTIATION
# * ###########################################################################
preparation_client = preparation.PreparationClient()

# * ###########################################################################
# * ASYNC CLASS INSTANTIATION
# * ###########################################################################
asynco_client = asynco.AsyncoClient()

# * ###########################################################################
# * ROUTE TO HOME
# * ###########################################################################
@app.route('/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def welcome():
    template = controller_client.render_index_page()
    return template

# * ###########################################################################
# * ROUTE TO OPEN POSITIONS TABLE
# * ###########################################################################
@app.route('/openpositions', methods=['GET', 'POST'])                                                                                  
def openpositions():
    checked_open_positions = database_client.get_checked_open_positions_firebase()

    if request.method == 'POST':
        data = []
        for openposition in checked_open_positions:
            asset = openposition["asset"]
            position_value_in_dollar = openposition["position_value_in_dollar"]
            netAsset = openposition["netAsset"]
            borrowed = openposition["borrowed"]
            free = openposition["free"]
            interest = openposition["interest"]
            locked = openposition["locked"]
            has_stop_loss = openposition["has_stop_loss"]
            side = openposition["side"]
            if has_stop_loss == "true":
                has_stop_loss = "<i class=\"far fa-thumbs-up\"></i>"
            else:
                has_stop_loss = "<i class=\"far fa-ban\"></i>"    
            icon = "<i class=\"cf cf-"+asset.lower()+"\"></i>"
            
            data.append({
                'asset': asset ,
                'side': side,
                'position_value_in_dollar': position_value_in_dollar ,
                'netAsset': netAsset ,
                'borrowed': borrowed ,
                'free': free ,
                'interest': interest ,
                'locked': locked ,
                'has_stop_loss': has_stop_loss ,
                'icon': icon 
            })
        
        response = {
            'aaData': data
        }
        return jsonify(response)

# * ###########################################################################
# * ROUTE TO OPEN ORDERS TABLE
# * ###########################################################################
@app.route('/openorders', methods=['GET', 'POST'])                                                                                  
def openorders():    

    if request.method == 'POST': 
        open_margin_orders = database_client.get_open_margin_orders_firebase()
        data = []
        for open_margin_order in open_margin_orders:
            symbol = open_margin_order["symbol"]
            side = open_margin_order["side"]
            quantity = open_margin_order["origQty"]
            stop_price = open_margin_order["stopPrice"]
            update_time = open_margin_order["updateTime"]
            order_id = open_margin_order["orderId"]
            data.append({
                'symbol': symbol ,
                'side': side ,
                'origQty': quantity ,
                'stopPrice': stop_price ,
                'updateTime': update_time ,
                'orderId': order_id
            })
        
        response = {
            'aaData': data
        }
        return jsonify(response)

# * ###########################################################################
# * ROUTE TO OPEN POSITIONS TABLE
# * ###########################################################################
@app.route('/recenttradehistory', methods=['GET', 'POST'])                                                                                  
def recenttradehistory():
    trade_history_list = []
    open_positions = database_client.get_checked_open_positions_firebase()
    for open_position in open_positions:
        symbol = open_position["asset"]
        if symbol != 'USDT' and symbol != 'BNB':
            symbol = symbol + 'USDT'
            tradehistory = exchange_client.get_margin_trades(symbol)
            trade_history_list.append(tradehistory[0])

    return jsonify(trade_history_list)

# * ###########################################################################
# * ROUTE TO OPEN POSITIONS TABLE
# * ###########################################################################
@app.route('/tradehistory', methods=['GET', 'POST'])                                                                                  
def tradehistory():
    trade_history_list = []
    open_positions = database_client.get_checked_open_positions_firebase()
    for open_position in open_positions:
        symbol = open_position["asset"]
        if symbol != 'USDT' and symbol != 'BNB':
            symbol = symbol + 'USDT'
            tradehistory = exchange_client.get_margin_trades(symbol)
            for trade in tradehistory:
                trade_history_list.append(trade)

    return jsonify(trade_history_list)

# * ###########################################################################
# * ROUTE TO WEBHOOK
# * ###########################################################################
@app.route('/webhook', methods=['GET', 'POST'])                                                                                  
async def get_data():
    data = {}
    try:
        data = json.loads(request.data)
    except Exception as e:
        print("an exception occurred - {}".format(e))
        return {"code": "error",
                "message": "Unable to read webhook"}
    # print(request.data)

    if data['password'] != config_client.PASSWORD:
        return {
            "code": "error",
            "message": "Nice try, invalid password"
        }

    interval = data['interval']
    coin_pair = data['ticker']
    signal = data['signal']
    logger.debug("⏭️ BEGIN OF WEBHOOK CALL ⏮️")
    logger.debug("ℹ️ interval:")
    logger.debug(interval )
    logger.debug("ℹ️ coin_pair:")
    logger.debug(coin_pair)
    logger.debug("ℹ️ signal:")
    logger.debug(signal)
    
    #present price from the market
    coin_price, btc_balance, btc_price, symbol_info, margin_account, open_margin_orders = await asynco_client.async_get_data(coin_pair)

    if coin_price != 0:
        if signal == "ENTRY LONG" or signal == "ENTRY SHORT":
            stop_price_from_tv = data['stopprice']
            entry_price_from_tv = data['entryprice']
            logger.debug("ℹ️ entry_price_from_tv:")
            logger.debug(entry_price_from_tv)
            logger.debug("ℹ️ stop_price_from_tv:")
            logger.debug(stop_price_from_tv)
            
            usdt_balance = preparation_client.get_usdt_balance(btc_balance, btc_price)
            logger.debug("ℹ️ usdt_balance:")   
            logger.debug(usdt_balance)     
            
            if signal == "ENTRY LONG":
                #prepare and open the long position
                sl_percent = round((1 - (stop_price_from_tv / entry_price_from_tv)), 4)
                logger.debug("ℹ️ sl_percent:")  
                logger.debug(sl_percent)    

                portion_size, risk_amount = preparation_client.portion_size(usdt_balance, sl_percent)
                logger.debug("ℹ️ portion_size:")
                logger.debug(portion_size)     
                logger.debug("ℹ️ risk_amount:")     
                logger.debug(risk_amount) 

                quantity = preparation_client.convert_portion_size_to_quantity(coin_price, portion_size)
                logger.debug("ℹ️ unrounded quantity:")  
                logger.debug(quantity)     

                rate_steps, quantity_steps = preparation_client.get_tick_and_step_size(symbol_info)
                logger.debug("ℹ️ rate_steps:") 
                logger.debug(rate_steps) 
                logger.debug("ℹ️ quantity_steps:")  
                logger.debug(quantity_steps)    

                quantity = preparation_client.rounding_exact_quantity(quantity, quantity_steps)
                logger.debug("ℹ️ rounded quantity:")  
                logger.debug(quantity)     
                
                order_response = await asynco_client.create_margin_order_entry_long(quantity, coin_pair)
                logger.debug("ℹ️ order_response:")  
                logger.debug(order_response)    

                #prepare and open the stop loss order
                trigger_condition = stop_price_from_tv
                stop_price = stop_price_from_tv * 0.999
                logger.debug("ℹ️ unrounded trigger_condition:") 
                logger.debug(trigger_condition) 
                logger.debug("ℹ️ unrounded stop_price:") 
                logger.debug(stop_price) 

                stop_price = preparation_client.rounding_exact_quantity(stop_price, rate_steps)
                trigger_condition = preparation_client.rounding_exact_quantity(trigger_condition, rate_steps)
                logger.debug("ℹ️ rounded trigger_condition:") 
                logger.debug(trigger_condition) 
                logger.debug("ℹ️ rounded stop_price:")
                logger.debug(stop_price)

                order_response_sl = await asynco_client.create_long_stop_loss_order(coin_pair,quantity,stop_price,trigger_condition)
                logger.debug("ℹ️ order_response_sl:")
                logger.debug(order_response_sl)
                logger.debug("ℹ️ END OF ENTRY LONG")
                
                #save the trade on the database
                database_client.set_order(order_response)
                open_date,side,entry_fee,present_price, dollar_size_entry = preparation_client.get_date_and_fees(order_response)
                present_price = preparation_client.rounding_exact_quantity(present_price, rate_steps)
                database_client.set_active_trade(coin_pair,open_date,interval,side,sl_percent,usdt_balance,risk_amount,portion_size,entry_price_from_tv, stop_price_from_tv, present_price, entry_fee, rate_steps, quantity_steps, dollar_size_entry)

            elif signal == "ENTRY SHORT":

                #prepare and open the long position
                sl_percent  = round(((stop_price_from_tv / entry_price_from_tv) - 1), 4)
                logger.debug("ℹ️ sl_percent:")  
                logger.debug(sl_percent)     

                portion_size, risk_amount = preparation_client.portion_size(usdt_balance, sl_percent)
                logger.debug("ℹ️ portion_size:")
                logger.debug(portion_size)     
                logger.debug("ℹ️ risk_amount:")     
                logger.debug(risk_amount)     

                quantity = preparation_client.convert_portion_size_to_quantity(coin_price, portion_size)
                logger.debug("ℹ️ unrounded quantity:")  
                logger.debug(quantity)    

                rate_steps, quantity_steps = preparation_client.get_tick_and_step_size(symbol_info)
                logger.debug("ℹ️ rate_steps:") 
                logger.debug(rate_steps) 
                logger.debug("ℹ️ quantity_steps:")  
                logger.debug(quantity_steps)       

                quantity = preparation_client.rounding_exact_quantity(quantity, quantity_steps)
                logger.debug("ℹ️ rounded quantity:")  
                logger.debug(quantity)      

                order_response = await asynco_client.create_margin_order_entry_short(quantity, coin_pair)
                logger.debug("ℹ️ order_response:")  
                logger.debug(order_response)    
                            
                #prepare and open the stop loss order
                trigger_condition = stop_price_from_tv
                stop_price = stop_price_from_tv * 1.001
                logger.debug("ℹ️ unrounded trigger_condition:") 
                logger.debug(trigger_condition) 
                logger.debug("ℹ️ unrounded stop_price:") 
                logger.debug(stop_price) 
                
                stop_price = preparation_client.rounding_exact_quantity(stop_price, rate_steps)
                trigger_condition = preparation_client.rounding_exact_quantity(trigger_condition, rate_steps)
                logger.debug("ℹ️ rounded trigger_condition:") 
                logger.debug(trigger_condition) 
                logger.debug("ℹ️ rounded stop_price:")
                logger.debug(stop_price)
                
                order_response_sl = await asynco_client.create_short_stop_loss_order(coin_pair,quantity,stop_price,trigger_condition)
                logger.debug("ℹ️ order_response_sl:")
                logger.debug(order_response_sl)
                logger.debug("ℹ️ END OF ENTRY SHORT")
                
                #save the trade on the database
                database_client.set_order(order_response)
                open_date,side,entry_fee,present_price, dollar_size_entry = preparation_client.get_date_and_fees(order_response)
                present_price = preparation_client.rounding_exact_quantity(present_price, rate_steps)
                database_client.set_active_trade(coin_pair,open_date,interval,side,sl_percent,usdt_balance,risk_amount,portion_size,entry_price_from_tv, stop_price_from_tv, present_price, entry_fee, rate_steps, quantity_steps, dollar_size_entry)

        elif signal == "EXIT LONG":
            quantity, order_id_list = preparation_client.check_is_sl_hit(coin_pair,open_margin_orders,margin_account)
            logger.debug("ℹ️ quantity:")
            logger.debug(quantity)
            logger.debug("ℹ️ order_id_list:")
            logger.debug(order_id_list)
            if len(order_id_list) == 0:
                logger.debug("ℹ️ coin_pair:")  
                logger.debug(coin_pair)  
                logger.debug("🔥 message: there is no position to exit on this pair🔥")
                return {
                    "code": "error",
                    "pair": coin_pair,
                    "message": "there is no position to exit on this pair"
                }
            else:
                for order_id in order_id_list:
                    logger.debug("ℹ️ order_id:") 
                    logger.debug(order_id) 
                    cancel_order_response = await asynco_client.cancel_margin_order(coin_pair,order_id)
                    logger.debug("ℹ️ cancel_order_response:")
                    logger.debug(cancel_order_response)
                
                order_response = await asynco_client.create_exit_long_order(coin_pair,quantity)
                logger.debug("ℹ️ order_response:")  
                logger.debug(order_response)  
                logger.debug("ℹ️ END OF EXIT LONG")
                
                if order_response != None:
                    database_client.set_exit_order(order_response)
                    database_client.set_closed_trade(order_response)
        elif signal == "EXIT SHORT":
            quantity, order_id_list = preparation_client.check_is_sl_hit_short(coin_pair,open_margin_orders,margin_account)
            logger.debug("ℹ️ quantity:")
            logger.debug(quantity)
            logger.debug("ℹ️ order_id_list:")
            logger.debug(order_id_list)
            if len(order_id_list) == 0:
                logger.debug("ℹ️ coin_pair:")  
                logger.debug(coin_pair)   
                logger.debug("🔥 message: there is no position to exit on this pair🔥")
                return {
                    "code": "error",
                    "pair": coin_pair,
                    "message": "there is no position to exit on this pair"
                }
            else:
                for order_id in order_id_list:
                    logger.debug("ℹ️ order_id:") 
                    logger.debug(order_id) 
                    cancel_order_response = await asynco_client.cancel_margin_order(coin_pair,order_id)
                    logger.debug("ℹ️ cancel_order_response:")
                    logger.debug(cancel_order_response)
                
                order_response = await asynco_client.create_exit_short_order(coin_pair,quantity)
                logger.debug("ℹ️ order_response:")  
                logger.debug(order_response)   
                logger.debug("ℹ️ END OF EXIT SHORT")
                if order_response != None:
                    database_client.set_exit_order(order_response)
                    database_client.set_closed_trade(order_response)
        else:
            logger.debug("ℹ️ signal:")  
            logger.debug(signal)  
            logger.debug("🔥 message: an error occurred, can read the signal 🔥")
            return "An error occurred, can read the signal"
    else:
            logger.debug("ℹ️ coin_pair:")
            logger.debug(coin_pair)   
            logger.debug("🔥 message: this is an invalid symbol 🔥")
            return {
                    "code": "error",
                    "pair": coin_pair,
                    "message": "this is an invalid symbol"
                }
    if order_response:
        return {
            "code": "success",
            "message": "order executed",
            "order_response": order_response
        }
    else:
        logger.debug("ℹ️ coin_pair:")
        logger.debug(coin_pair)
        logger.debug("ℹ️ interval:") 
        logger.debug(interval)
        logger.debug("ℹ️ signal:")  
        logger.debug(signal)  
        logger.debug("🔥 message: order failed 🔥")
        return {
            "code": "error",
            "message": "order failed"

        }
    return jsonify(data)