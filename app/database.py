from app import config
from app import preparation
import sys
import logging
from datetime import datetime
import firebase_admin
from firebase_admin import firestore

# * ###########################################################################
# * LOGGING INSTANTIATION RETURNING ON CONSOLE
# * ###########################################################################
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# * ###########################################################################
# * CONFIG INSTANTIATION RETURNING ON CONSOLE
# * ###########################################################################
vault = config.ConfigClient()

# * ###########################################################################
# * PREPARATION CLASS INSTANTIATION
# * ###########################################################################
preparation_client = preparation.PreparationClient()

# * ###########################################################################
# * FIREBASE INITIALIZATION
# * ###########################################################################
firebase_admin.initialize_app()

# * ###########################################################################
# * Class ExchangeClient
class DatabaseClient:
    # * #######################################################################
    # * Class initialization
    def __init__(self):
        self.base_currency = "BTCUSDT"

    # * #######################################################################
    # * Function     
    def get_open_margin_orders_firebase(self):
        print("🚀 RUNNING get_open_margin_orders ---------------")
        db = firestore.Client()
        docs = []
        open_margin_orders_collection = db.collection(u'open_margin_orders').stream()
        for doc in open_margin_orders_collection:
            open_margin_orders = doc.to_dict()
            open_order = open_margin_orders["open_order"]
            docs.append(open_order)
        return docs

    # * #######################################################################
    # * Function     
    def get_checked_open_positions_firebase(self):
        print("🚀 RUNNING get_checked_open_positions_firebase ---------------")
        db = firestore.Client()
        docs = []
        checked_open_positions_collection = db.collection(u'checked_open_positions').stream()
        for doc in checked_open_positions_collection:            
            docs.append(doc.to_dict())
        return docs

    # * #######################################################################
    # * Function get_active_trades   
    def get_active_trades(self):
        db = firestore.Client()
        docs = []
        active_trades_stream = db.collection(u'active_trades').stream()
        for doc in active_trades_stream:
            docs.append(doc.to_dict())
        return docs

    # * #######################################################################
    # * Function 
    def delete_open_margin_orders(self):
        db = firestore.Client()

        # [START firestore_data_delete_collection]
        def delete_collection(coll_ref, batch_size):
            docs = coll_ref.limit(batch_size).stream()
            deleted = 0

            for doc in docs:
                print(f'Deleting doc {doc.id} => {doc.to_dict()}')
                doc.reference.delete()
                deleted = deleted + 1

            if deleted >= batch_size:
                return delete_collection(coll_ref, batch_size)
        # [END firestore_data_delete_collection]

        delete_collection(db.collection(u'open_margin_orders'), 10)

    # * #######################################################################
    # * Function     
    def delete_checked_open_positions(self):
        db = firestore.Client()

        # [START firestore_data_delete_collection]
        def delete_collection(coll_ref, batch_size):
            docs = coll_ref.limit(batch_size).stream()
            deleted = 0

            for doc in docs:
                print(f'Deleting doc {doc.id} => {doc.to_dict()}')
                doc.reference.delete()
                deleted = deleted + 1

            if deleted >= batch_size:
                return delete_collection(coll_ref, batch_size)
        # [END firestore_data_delete_collection]

        delete_collection(db.collection(u'checked_open_positions'), 10)

    # * #######################################################################
    # * Function 
    def set_active_trade(self, coin_pair, date_open, timeframe, side, stop_loss_pct, account_balance, risk_amount, position_size, entry_price, signal_stop_loss_price, present_price, entry_fee, rate_steps, quantity_steps, dollar_size_entry):
            
        db = firestore.Client()
        active_trade_document = db.collection(u'active_trades').document(coin_pair)   

        try:
            active_trade_document.set(
                {
                    u'coin_pair': coin_pair,
                    u'date_open': date_open,
                    u'timeframe': timeframe,
                    u'side': side,
                    u'stop_loss_pct': stop_loss_pct,
                    u'account_balance': account_balance,
                    u'risk_amount': risk_amount,
                    u'position_size': position_size,
                    u'signal_entry_price': entry_price,
                    u'signal_stop_loss_price': signal_stop_loss_price,
                    u'trade_entry_price': present_price,
                    u'entry_fee': entry_fee,
                    u'rate_steps': rate_steps,
                    u'quantity_steps': quantity_steps,
                    u'dollar_size_entry': dollar_size_entry
                }
            )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False

        return {
            logger.debug("👇👇👇👇👇 - set_active_trade successful - 👇👇👇👇👇 ")   
        }

    # * #######################################################################
    # * Function set_closed_trade
    def set_closed_trade(self,exit_order_response):
            
        db = firestore.Client()
 
        active_trades = self.get_active_trades()  
        this_trade = None 
        for active_trade in active_trades:
            if active_trade["coin_pair"] == exit_order_response["symbol"]:
                this_trade = active_trade

        try:
            #data from ENTRY ORDER
            rate_steps = this_trade["rate_steps"] 
            date_entry = this_trade["date_open"]            
            timeframe = this_trade["timeframe"]
            side_entry = this_trade["side"]
            stop_loss_pct = this_trade["stop_loss_pct"]
            account_balance = this_trade["account_balance"]
            risk_amount = this_trade["risk_amount"]
            signal_entry_price = this_trade["signal_entry_price"]
            signal_stop_loss_price = this_trade["signal_stop_loss_price"]
            trade_entry_price = this_trade["trade_entry_price"] 
            fee_entry = this_trade["entry_fee"] 
            dollar_size_entry = this_trade["dollar_size_entry"] 
            
            #data from EXIT ORDER            
            symbol = exit_order_response["symbol"]
            transactTime = exit_order_response["transactTime"]
            position_size = exit_order_response["origQty"]
            dollar_size_exit = float(exit_order_response["cummulativeQuoteQty"])
            trade_exit_price = dollar_size_exit/float(position_size)
            trade_exit_price = preparation_client.rounding_exact_quantity(trade_exit_price,rate_steps)
            date_exit, side_exit, fee_exit = preparation_client.get_exit_date_and_fees(exit_order_response)

            #final P&L calculation
            p_and_l_pct = (dollar_size_exit / dollar_size_entry) - 1
            p_and_l_pct = "{:.5%}".format(p_and_l_pct)
            p_and_l_dollar = dollar_size_exit - dollar_size_entry
            p_and_l_dollar = round(p_and_l_dollar,2)

            #prepare the firestore object
            closed_trade_id = str(transactTime) + "-"+ symbol
            closed_trade_document = db.collection(u'closed_trades').document(closed_trade_id) 
            active_trade_document = db.collection(u'active_trades').document(symbol)
                        
            closed_trade_document.set(
                {
                    u'symbol': symbol,
                    u'date_entry': date_entry,
                    u'date_exit': date_exit,
                    u'timeframe': timeframe,
                    u'side_entry': side_entry,
                    u'side_exit': side_exit,
                    u'account_balance': account_balance,
                    u'risk_amount': risk_amount,
                    u'position_size': position_size,
                    u'signal_entry_price': signal_entry_price,
                    u'signal_stop_loss_pct': stop_loss_pct,
                    u'signal_stop_loss_price': signal_stop_loss_price,
                    u'trade_entry_price': trade_entry_price,
                    u'trade_exit_price': trade_exit_price,
                    u'fee_entry': fee_entry,
                    u'fee_exit': fee_exit,
                    u'dollar_size_entry': dollar_size_entry,
                    u'dollar_size_exit': dollar_size_exit,
                    u'p_and_l_pct': p_and_l_pct,
                    u'p_and_l_dollar': p_and_l_dollar
                }
            )
            active_trade_document.delete()
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False

        return {
            logger.debug("👇👇👇👇👇 - set_closed_trade successful - 👇👇👇👇👇 ")   
        }

    # * #######################################################################
    # * Function     
    def set_exit_order(self, order_response):
        
        exit_order_id = str(order_response["transactTime"])+"-"+order_response["symbol"]
        db = firestore.Client()
        exit_order = db.collection(u'exit_order').document(exit_order_id)
        now = datetime.now()
        now = preparation_client.format_time(now)

        try:
            exit_order.set(
                {
                    u'order_response': order_response,
                    u'time_now': now,
                }
            )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False
        return {
            print(exit_order)
        }

    # * #######################################################################
    # * Function 
    def set_order(self, order_response):        
        entry_order_id = str(order_response["transactTime"])+"-"+order_response["symbol"]
        db = firestore.Client()
        entry_order = db.collection(u'entry_order').document(entry_order_id)
        now = datetime.now()
        now = preparation_client.format_time(now)     
        try:
            entry_order.set(
                {
                    u'order_response': order_response,
                    u'time_now': now,
                }
            )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False
        return {
            print(entry_order)
        }

    # * #######################################################################
    # * Function 
    def set_account_overview(self, account_overview):
        db = firestore.Client()
        account_overview_id = "user"
        entry_order = db.collection(u'account_overview').document(account_overview_id)
        now = datetime.now()
        now = preparation_client.format_time(now)
        try:
            entry_order.set(
                {
                    u'account_overview': account_overview,
                    u'time_now': now,
                }
            )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False
        return {
            print(account_overview)
        }

    # * #######################################################################
    # * Function     
    def set_open_margin_orders(self, open_margin_orders):
        
        db = firestore.Client()
        self.delete_open_margin_orders()
        try:
            for open_order in open_margin_orders:
                open_order_id = str(open_order["transact_time"]) + "-" + open_order["symbol"]
                open_margin_orders_collection = db.collection(u'open_margin_orders').document(open_order_id) 
                open_margin_orders_collection.set(
                    {
                        u'open_order': open_order
                    }
                )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False
        return {
            logger.debug("👇👇👇👇👇 - set_open_margin_orders successful - 👇👇👇👇👇 ")   
        }

    # * #######################################################################
    # * Function 
    def set_checked_open_position(self, open_position):
            
        db = firestore.Client()        
        checked_open_positions_collection = db.collection(u'checked_open_positions').document(open_position['asset'])
        try:
            checked_open_positions_collection.set(
                {
                    u'asset': open_position['asset'] ,
                    u'position_value_in_dollar': open_position['position_value_in_dollar'] ,
                    u'netAsset': open_position['netAsset'] ,
                    u'borrowed': open_position['borrowed'] ,
                    u'free': open_position['free'] ,
                    u'interest': open_position['interest'] ,
                    u'locked': open_position['locked'] ,
                    u'has_stop_loss': open_position['has_stop_loss'] ,
                    u'side': open_position['side'] ,
                    u'icon': None 
                }
            )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False
        return {
            logger.debug("👇👇👇👇👇 - set_checked_open_positions successful - 👇👇👇👇👇 ")   
        }    

    # * #######################################################################
    # * Function 
    def set_tradable_assets(self, tradable_list):
            
        db = firestore.Client()
        now = datetime.now()
        now = preparation_client.format_time(now)
        try:
            for tradable_asset in tradable_list:
                tradable_assets = db.collection(u'tradable_assets').document(tradable_asset)
                tradable_assets.set(
                    {
                        u'tradable_asset': tradable_asset,
                        u'time_now': now,
                    }
                )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False

        return {
            print(tradable_assets)
        }