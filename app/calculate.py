from app import config
import json
from datetime import datetime
from binance.client import Client
from binance.enums import *
import logging
import math

# * ###########################################################################
# * LOGGING INSTATIATION RETURNING ON CONSOLE
# * ###########################################################################
logger = logging.getLogger(__name__)

# * ###########################################################################
# * CONFIG CLASS INSTATIATION
# * ###########################################################################
config_client = config.ConfigClient()

# * ###########################################################################
# * Class CalculateClient
class CalculateClient:
    def __init__(self):
        self.RISK_FACTOR = 0.01
        self.client = Client(config_client.API_KEY, config_client.API_SECRET)
        self.now = datetime.now()

    def portion_size(self, account_balance, stop_limit_percentage):
        risk_amount = account_balance * self.RISK_FACTOR
        portion_size = risk_amount / stop_limit_percentage
        return self.rounding_quantity(portion_size)

    def rounding_quantity(self, quantity):

        if quantity > 1000:
            return round(quantity, 0)
        elif quantity > 100:
            return round(quantity, 1)
        elif quantity > 10:
            return round(quantity, 1)
        elif quantity > 1:
            return round(quantity, 2)  # Change while not in DEV
        else:
            return round(quantity, 3)

    def convert_portion_size_to_quantity(self, coin_pair, portion_size):
        try:

            coin_rate = float(
                (self.client.get_symbol_ticker(symbol=coin_pair)['price']))
            quantity = portion_size / coin_rate
            return self.rounding_quantity(quantity)

        except Exception as e:
            print("an exception occured - {}".format(e))

    def update_current_profit(self):
        current_profit = 0
        running_trades = self.get_running_trades()
        for time_id, values in running_trades.items():
            coinpair = values["coinpair"]
            side = values["side"]
            current_rate = self.get_current_rate(coinpair)
            quantity = values["quantity"]
            portion_size = values["portion_size"]
            current_profit = current_rate * \
                float(quantity) - float(portion_size)
            if side == "SHORT":
                current_profit *= -1
            running_trades[time_id]["current_profit"] = int(current_profit)

        try:
            with open("running_trades.json", "w") as outfile:
                json.dump(running_trades, outfile, indent=2)

        except Exception as e:
            print("an exception occured - {}".format(e))

    def get_asset_USDT(self):
        try:
            _len = len(self.client.get_margin_account()["userAssets"])
            for x in range(_len):
                if self.client.get_margin_account()["userAssets"][x]["asset"] == "USDT":
                    balance_USDT = self.client.get_margin_account()[
                        "userAssets"][x]["free"]
                    return balance_USDT
        except Exception as e:
            print("an exception occured - {}".format(e))

        return 0

    def finding_quantity_and_ID_from_running_trades_rec(self,find_coin, find_interval):
        print(find_coin, find_interval)
        found_quantity = 0
        found_time_id = ""
        try:
            with open("running_trades.json") as file:
                running_orders = json.load(file)
            for time_id, values in running_orders.items():
                for key in values:
                    print(values[key])
                    if values[key] == find_coin:
                        found_quantity = values["quantity"]
                        found_time_id = time_id
            if found_quantity == 0:
                return 0, "No ID found"
            return found_quantity, found_time_id
        except Exception as e:
            print("an exception occured - {}".format(e))
            return 0, "No ID found"

    def append_running_trades(self, coinpair, interval, quantity, portion_size, side, sl_id):
        now = datetime.now()

        try:
            with open("running_trades.json") as file:

                running_orders = json.load(file)

            with open("running_trades.json", "w") as outfile:
                time_now = str(now.strftime("%d/%m %H:%M:%S"))
                coin_rate = float(
                    (self.client.get_symbol_ticker(symbol=coinpair)['price']))
                self.rounding_quantity(coin_rate)
                running_orders[time_now] = {"coinpair": coinpair, "interval": interval, "quantity": quantity,
                                            "portion_size": portion_size, "side": side, "rate": coin_rate,
                                            "sl_id": sl_id}
                json.dump(running_orders, outfile, indent=2)  # dump
                # append_running_trades_firestore(
                #     coinpair, interval, quantity, portion_size, side, coin_rate, sl_id)

        except Exception as e:
            print("an exception occured - {}".format(e))

    def get_running_trades(self):
        try:

            with open("running_trades.json") as file:
                return json.load(file)
        except Exception as e:
            print("an exception occured - {}".format(e))

    def append_all_trades(self, coinpair, interval, quantity, portion_size, side, profit):

        side = "LONG"
        try:
            now = datetime.now()
            with open("all_trades.json") as file:
                all_trades = json.load(file)

            with open("all_trades.json", "w") as outfile:
                time_now = str(now.strftime("%d/%m %H:%M:%S"))
                all_trades[time_now] = {"coinpair": coinpair, "interval": interval, "quantity": quantity,
                                        "portion_size": portion_size, "side": side, "Profit": profit}
                json.dump(all_trades, outfile, indent=2)
                # append_all_trades_firestore(
                #     coinpair, interval, quantity, portion_size, side, profit)
        except Exception as e:
            print("an exception occured - {}".format(e))

    def get_total_profit(self):
        profit = 0
        try:
            with open("all_trades.json") as file:
                all_trades = json.load(file)

                for key in all_trades:
                    for value in all_trades[key]:
                        if value == "Profit":
                            profit += all_trades[key]["Profit"]
        except Exception as e:
            print("Cant get total profit, an exception occured - {}".format(e))
            return 0
        else:
            return profit

    def get_all_trades(self):
        try:

            with open("all_trades.json") as file:

                return json.load(file)
        except Exception as e:
            print("an exception occured - {}".format(e))

    def long_order(self, side, quantity, coinpair, interval, portionsize, exit_price, sl_percentage):
        order_type = ORDER_TYPE_MARKET
        if side == "BUY":
            try:
                rate_steps, quantity_steps = self.get_tick_and_step_size(coinpair)
                quantity = self.rounding_exact_quantity(quantity, quantity_steps)
                time_now = str(self.now.strftime("%d/%m %H:%M:%S"))
                print(f"sending order: {time_now} {coinpair} quantity: {quantity} "
                    f"portion size: {portionsize} SL % : {sl_percentage} ")
                order = self.client.create_margin_order(sideEffectType="MARGIN_BUY", symbol=coinpair, side=side, type=ORDER_TYPE_MARKET, quantity=quantity)

            except Exception as e:
                print("an exception occured - {}".format(e))
                return False

            else:
                side = "LONG"
                sl_id = self.set_sl(exit_price, coinpair, quantity, side)
                self.append_running_trades(
                    coinpair, interval, quantity, self.rounding_quantity(portionsize), side, sl_id)
                return order

        elif side == "SELL":
            print(coinpair, interval)
            previous_quanities, time_id = self.finding_quantity_and_ID_from_running_trades_rec(coinpair, interval)
            print("pre Q: ", previous_quanities)
            if time_id == "No ID found":
                print("no ID found, ID= ", time_id)
                return False

            running_trades = self.get_running_trades()
            sl_id = running_trades[time_id]["sl_id"]
            self.check_is_sl_hit(coinpair, sl_id)
            rounded_down_quantity = self.rounding_quantity(
                float(previous_quanities) * 0.999)
            try:
                print("sending order: ", order_type, side,
                      rounded_down_quantity, coinpair)
                order = self.client.create_margin_order(sideEffectType="AUTO_REPAY", symbol=coinpair, side=side,
                                                        type=ORDER_TYPE_MARKET, quantity=rounded_down_quantity)

            except Exception as e:
                print("an exception occured - {}".format(e))
                return False

            else:
                usdt_rate = float(self.client.get_symbol_ticker(
                    symbol=coinpair)['price'])
                exit_portion_size = self.rounding_quantity(
                    usdt_rate * rounded_down_quantity)
                with open("running_trades.json") as file:
                    running_trades = json.load(file)

                entry_portion_size = running_trades[time_id]["portion_size"]
                profit = self.rounding_quantity(
                    float(exit_portion_size) - float(entry_portion_size))
                self.append_all_trades(
                    coinpair, interval, previous_quanities, entry_portion_size, side, profit)
                self.delete_running_trades(time_id)
                return order

    def delete_running_trades(self, time_id):
        running_trades = {}
        try:
            with open("running_trades.json") as file:
                running_trades = json.load(file)
                del running_trades[time_id]

            with open("running_trades.json", "w") as outfile:
                json.dump(running_trades, outfile, indent=2)

        except Exception as e:
            print("an exception occured - {}".format(e))

    def get_current_rate(self, coinpair):
        current_rate = float(
            (self.client.get_symbol_ticker(symbol=coinpair)['price']))
        return current_rate

    def get_usdt_balance(self):
        btc_balance = float(self.client.get_margin_account()[
                            'totalNetAssetOfBtc'])
        btc_rate = float(
            (self.client.get_symbol_ticker(symbol="BTCUSDT")['price']))
        usdt_balance = round(btc_balance * btc_rate, 0)
        return int(usdt_balance)

    def get_total_current_profit(self):
        running_trades = self.get_running_trades()
        total_current_profit = 0
        for time_id, values in running_trades.items():
            total_current_profit += values["current_profit"]
            # print(values["current_profit"])
        return total_current_profit

    def set_sl(self, exit_sl, coinpair, quantity, side):
        if side == "LONG":
            limit_price = exit_sl * 0.97
            rate_steps, quantity_steps = self.get_tick_and_step_size(coinpair)
            exit_sl = self.rounding_exact_quantity(exit_sl, rate_steps)
            limit_price = self.rounding_exact_quantity(limit_price, rate_steps)
            quantity = self.rounding_exact_quantity(float(quantity) * 0.97, quantity_steps)
            side = SIDE_SELL
        elif side == "SHORT":
            limit_price = exit_sl * 1.02
            rate_steps, quantity_steps = self.get_tick_and_step_size(coinpair)
            exit_sl = self.rounding_exact_quantity(exit_sl, rate_steps)
            limit_price = self.rounding_exact_quantity(limit_price, rate_steps)
            quantity = self.rounding_exact_quantity(float(quantity) * 0.97, quantity_steps)
            side = SIDE_BUY
        try:
            print("Sending SL order:", coinpair, side,
                  "Q: ", quantity, "stopPrice", exit_sl)
            order = self.client.create_margin_order(
                symbol=coinpair,
                side=side,
                type=ORDER_TYPE_STOP_LOSS_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                price=limit_price,
                stopPrice=exit_sl
            )
        except Exception as e:
            print("No SL could be set: - {}".format(e))
            return "No SL could be set"

        order_id = order["orderId"]
        return order_id

    def check_is_sl_hit(self, coinpair, sl_id):

        try:
            if self.client.get_margin_order(
                    symbol=coinpair,
                    orderId=sl_id):
                self.client.cancel_margin_order(
                    symbol=coinpair,
                    orderId=sl_id)

        except Exception as e:
            print("No SL could be set: - {}".format(e))

    def short_order(self, side, quantity, coinpair, interval, portionsize, exit_price, sl_percent):
        order_type = ORDER_TYPE_MARKET
        if side == "SELL":

            try:
                print(f"sending order: SHORT - {order_type} - {side} {quantity} {coinpair}")
                order = self.client.create_margin_order(sideEffectType="MARGIN_BUY", symbol=coinpair, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=quantity)

            except Exception as e:
                print("an exception occured - {}".format(e))
                return False
            else:
                side = "SHORT"
                sl_id = self.set_sl(exit_price, coinpair, quantity, side)

                self.append_running_trades(coinpair, interval, quantity, self.rounding_quantity(portionsize), side, sl_id, sl_percent)
                self.update_current_profit()
                return order

        elif side == "BUY":
            previous_quanities, time_id = self.finding_quantity_and_ID_from_running_trades_rec(coinpair, interval)
            print("Q ", previous_quanities, "ID ", time_id)
            if time_id == "No ID found":
                print("no ID found, ID= ", time_id)
                return False

            running_trades = self.get_running_trades()
            sl_id = running_trades[time_id]["sl_id"]
            self.check_is_sl_hit(coinpair, sl_id)
            rounded_down_quantity = self.rounding_quantity(float(previous_quanities) * 0.999)
            try:
                print("sending order: ", order_type, side, rounded_down_quantity, coinpair)
                order = self.client.create_margin_order(sideEffectType="AUTO_REPAY",
                                                        symbol=coinpair, side=SIDE_BUY, type=ORDER_TYPE_MARKET,
                                                        quantity=rounded_down_quantity)

            except Exception as e:
                print("an exception occured - {}".format(e))
                return False

            else:
                usdt_rate = float(self.client.get_symbol_ticker(symbol=coinpair)['price'])
                exit_portion_size = self.rounding_quantity(usdt_rate * rounded_down_quantity)
                with open("running_trades.json") as file:
                    running_trades = json.load(file)
                entry_portion_size = running_trades[time_id]["portion_size"]
                profit = self.rounding_quantity(float(exit_portion_size) - float(entry_portion_size))

                self.append_all_trades(coinpair, interval, previous_quanities, entry_portion_size, side, profit)
                self.delete_running_trades(time_id)
                return order

    
    # def get_Active_Trades(self):
    #     print("🚀 ENTROU readRunningTrades ---------------")
    #     db = firestore.Client()
    #     docs = []
    #     runningTradesData = db.collection(u'active_trades').stream()
    #     for doc in runningTradesData:
    #         print("🚀 ENTROU no SIDE do readRunningTrades -------")
    #         print(doc.get('side'))
    #         print("🚀 ENTROU no SIDE do readRunningTrades -------")
    #         docs.append(doc.to_dict())
    #     return docs

    # def get_Closed_Trades(self):
    #     print("🚀 ENTROU readTradeObject ---------------")
    #     db = firestore.Client()
    #     trades = []
    #     trades_doc_ref_list = db.collection(u'closed_trades').stream()
    #     for trade_doc_ref in trades_doc_ref_list:
    #         print("🚀 ENTROU no FOR do get_TradeObject_List -------")
    #         # trade_doc = trade_doc_ref.get(trade_doc_ref.id)
    #         trade = Trade.from_dict(trade_doc_ref.to_dict())
    #         print(trade)
    #         print("🚀 ENTROU no FOR do get_TradeObject_List -------")
    #         trades.append(trade)
    #     return trades
        # Check how many decimals are allowed per coinpair, 
        # tickSize = allowed decimals in price range
        # stepSize = allowed decimals in quantity range

    def get_tick_and_step_size(self, symbol):
        tick_size = None
        step_size = None
        symbol_info = self.client.get_symbol_info(symbol)
        for filt in symbol_info['filters']:
            if filt['filterType'] == 'PRICE_FILTER':
                tick_size = float(filt['tickSize'])
            if filt['filterType'] == 'LOT_SIZE':
                step_size = float(filt['stepSize'])
        return tick_size, step_size

        # Round the quantity or price range, with the actual allowed decimals
    def rounding_exact_quantity(self, quantity, step_size):
        print("stepSize", step_size)
        step_size = int(math.log10(1 / float(step_size)))
        quantity = math.floor(float(quantity) * 10 ** step_size) / 10 ** step_size
        quantity = "{:0.0{}f}".format(float(quantity), step_size)
        return str(int(quantity)) if int(step_size) == 0 else quantity

# def append_running_trades_firestore(coinpair, interval, quantity, portion_size, side, coin_rate, sl_id):

#     db = firestore.Client()
#     newTrade = db.collection(u'active_trades').document()
#     newActivity = db.collection(u'activity').document()
#     now = datetime.now()

#     try:
#         newTrade.set(
#             {
#                 u'coinpair': coinpair,
#                 u'interval': interval,
#                 u'quantity': quantity,
#                 u'portion_size': portion_size,
#                 u'side': side,
#                 u'coin_rate': coin_rate,
#                 u'sl_id': sl_id,
#                 u'time_now': now.strftime("%m/%d/%Y, %H:%M:%S"),
#             }
#         )  # wait for table load to complete.
#         newActivity.set(
#             {
#                 u'text': 'A new trade was made',
#                 u'side': side,
#                 u'time': now.strftime("%m/%d/%Y, %H:%M:%S"),
#             }
#         )
#     except Exception as e:
#         print("an exception occured - {}".format(e))
#         return False

#     return {
#         print(coinpair+" "+interval+" "+quantity+" " +
#               portion_size+" "+side+" "+coin_rate+" "+sl_id)
#     }


# def append_all_trades_firestore(coinpair, interval, quantity, portion_size, side, profit):

#     db = firestore.Client()
#     newTrade = db.collection(u'closed_trades').document()
#     newActivity = db.collection(u'activity').document()
#     now = datetime.now()

#     try:
#         newTrade.set(
#             {
#                 u'coinpair': coinpair,
#                 u'interval': interval,
#                 u'quantity': quantity,
#                 u'portion_size': portion_size,
#                 u'side': side,
#                 u'coin_rate': profit,
#                 u'time_now': now.strftime("%m/%d/%Y, %H:%M:%S"),
#             }
#         )  # wait for table load to complete.
#         newActivity.set(
#             {
#                 u'text': 'A new trade was made',
#                 u'side': side,
#                 u'time_now': now.strftime("%m/%d/%Y, %H:%M:%S"),
#             }
#         )
#     except Exception as e:
#         print("an exception occured - {}".format(e))
#         return False

#     return {
#         print(coinpair+" "+interval+" "+quantity +
#               " "+portion_size+" "+side+" "+profit)
#     }

# [START custom_class_def]
# [START firestore_data_custom_type_definition]
class Trade(object):
    def __init__(self, coinpair, interval, quantity, portion_size, side, coin_rate, date):
        self.coinpair = coinpair
        self.interval = interval
        self.quantity = quantity
        self.portion_size = portion_size
        self.side = side
        self.coin_rate = coin_rate
        self.date = date

    @staticmethod
    def from_dict(source):
        # [START_EXCLUDE]
        trade = Trade(source[u'coinpair'], source[u'interval'], source[u'quantity'], source[u'portion_size'], source[u'side'],source[u'coin_rate'],source[u'time_now'])
        # [END_EXCLUDE]

    def to_dict(self):
        # [START_EXCLUDE]
        dest = {
            u'coinpair': self.coinpair,
            u'interval': self.interval,
            u'quantity': self.quantity,
            u'coin_rate': self.coin_rate,
            u'side': self.side,
            u'portion_size': self.portion_size
        }

        if self.time_now:
            dest[u'time_now'] = self.time_now

        return dest
        # [END_EXCLUDE]

    def __repr__(self):
        return(
            f'Trade(\
                coinpair={self.coinpair}, \
                interval={self.interval}, \
                quantity={self.quantity}, \
                portion_size={self.portion_size}, \
                side={self.side}, \
                coin_rate={self.coin_rate}, \
                time_now={self.time_now}\
            )'
        )    
# [END firestore_data_custom_type_definition]
# [END custom_class_def]
