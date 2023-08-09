import datetime as dt
from pya3 import *
import math
from .send_message import send_email, send_msg
import sys
import numpy as np
import pandas as pd
import bisect

def latest_expiry(trading_symbol):
    symboldf = pd.read_csv('https://api.kite.trade/instruments')
    pd.options.mode.chained_assignment = None
    df = symboldf[(symboldf.exchange == 'NFO') & (symboldf.name == trading_symbol)  & (symboldf.segment == 'NFO-OPT')]
    df['expiry'] = pd.to_datetime(df['expiry']).apply(lambda x: x.date())
    df.drop(df[df.expiry <datetime.now().date()].index, inplace=True)
    weekly_expiry = df[df.segment == 'NFO-OPT']['expiry'].unique().tolist()
    weekly_expiry.sort()
    return str(weekly_expiry[0])

# print(latest_expiry("BANKNIFTY"))
def round_nearest(x, num=50): return int(math.ceil(float(x)/num)*num)
def round_100(x): return round_nearest(x, 100)
def round_50(x): return round_nearest(x, 50)
def strRed(skk):         return "\033[91m {}\033[00m".format(skk)
def strGreen(skk):       return "\033[92m {}\033[00m".format(skk)
def strLightPurple(skk): return "\033[94m {}\033[00m".format(skk)
def strBold(skk):        return "\033[1m {}\033[0m".format(skk)

def get_ltp_info(alice,instrument):
	for i in range(30):
		# print("ltp")
		try:
			# print("ltp1")
			ltp = alice.get_scrip_info(instrument)['Ltp']
			return ltp
		except Exception as e:
			print("ERROR IN LTP FETCH-> ",{e})
			sleep(2)
			pass

def monthly_expiry(trading_symbol):
    df = pd.read_csv('https://api.kite.trade/instruments')
    df = df[(df.exchange == 'NFO') & (df.name == trading_symbol)  & (df.instrument_type == 'FUT')]
    df['expiry'] = pd.to_datetime(df['expiry']).apply(lambda x: x.date())
    df.drop(df[df.expiry <datetime.now().date()].index, inplace=True)
    weekly_expiry = df['expiry'].unique().tolist()
    weekly_expiry.sort()
    return weekly_expiry[0]

def get_oid(order_placed_output):
    oid = order_placed_output['NOrdNo']
    return oid

def get_order_status(alice,number):
    order_status= None
    sleep(1)
    for i in range(11):
        # print("Trying to get order status")
        try:
            # print("try",i)
            order_details = alice.get_order_history(str(number))
            order_status = order_details['Status']
            return order_status
        except Exception as e:
            print("ORDER STATUS ERROR:",{e})
            sleep(10)
            pass

def ap_generator(alice,oid):
    print("UNDER AP GENERATOR")
    sleep(1)
    for i in range(11):
        try:
            order_details = alice.get_order_history(str(oid))
            avg_price = float(order_details['Avgprc'])
            return avg_price
        except Exception as e:
            print("AVG PRC ERROR:",{e})
            sleep(10)
            pass


def generate_session(alice,username):
    session_id = alice.get_session_id()
    print(session_id)
    # if session_id['session_id'] not in session_id:
    # if session_id['apikey'] == None:
    if 'sessionID' not in session_id:
        for i in range(2):
            sleep(4)
            print("Retrying session generation! Loop->",i)
            session_id = alice.get_session_id()

        # if session_id['apikey'] == None:
        if 'sessionID' not in session_id:
            msg = ("Session generation is pending for",username)
            send_msg(msg)
            print(msg)
            sys.exit()
    else:
        print("SESSION GENERATED SUCCESSFULY!")

def check_margin(alice,client_code,username,no_of_lots,required_margin,user_gmail_id):
    net_margin = int(float(alice.get_balance()[0]["net"]))
    print("MARGIN AVAILABLE FOR TRADING IS ",net_margin)
    required_margin_amt = no_of_lots* required_margin
    if net_margin >= required_margin_amt:
        print("SUFFICIENT MARGIN!")
    else:
        msg = ("Margin Shortfall for user->",username,"\n Net Margin required is->",required_margin_amt,"\n Available margin is->",net_margin)
        print(msg)
        send_email(user_gmail_id,client_code,username,msg)
        send_msg(msg)
        sys.exit()


def order_modify_put(alice,oid,inst):
	order_details = alice.get_order_history(oid)
	order_status = order_details['Status']
	print("put slm order status",order_status)
	if order_status == 'trigger pending':
		modify_slm_put = alice.modify_order(transaction_type=TransactionType.Buy, instrument=inst, product_type=ProductType.Intraday, order_id=str(oid), order_type=OrderType.Market,quantity=quantity)
	else:
		print("Order is either cancelled or completed")

def order_modify_call(alice,oid,inst):
	order_details = alice.get_order_history(oid)
	order_status = order_details['Status']
	print("call slm order status",order_status)
	if order_status == 'trigger pending':
		modify_slm_call = alice.modify_order(transaction_type=TransactionType.Buy, instrument=inst, product_type=ProductType.Intraday, order_id=str(oid), order_type=OrderType.Market,quantity=quantity)
	else:
		print("Order is either cancelled or completed")


def modify_ce_order_to_cost(alice,inst,pe_sl_oid, call_sell_avg_price,quantity):
    ce_sl_cost_price = 0.05 * round((float(call_sell_avg_price))/0.05)
    modify_ce_to_cost = alice.modify_order(transaction_type=TransactionType.Buy, instrument=inst, product_type=ProductType.Intraday, order_id=str(pe_sl_oid), order_type=OrderType.StopLossLimit,quantity=quantity,price = ce_sl_cost_price + 10,trigger_price = ce_sl_cost_price)
    print(modify_ce_to_cost)
    print("CE order modified")

def modify_pe_order_to_cost(alice,inst,ce_sl_oid,put_sell_avg_price,quantity):  
    pe_sl_cost_price = 0.05 * round((float(put_sell_avg_price))/0.05)
    modify_pe_to_cost = alice.modify_order(transaction_type=TransactionType.Buy, instrument=inst, product_type=ProductType.Intraday, order_id=str(ce_sl_oid), order_type=OrderType.StopLossLimit,quantity=quantity,price = pe_sl_cost_price + 10,trigger_price = pe_sl_cost_price)
    print(modify_pe_to_cost)
    print("PE order modified")

def above_closest_value(lst, target):
    above_closest = None
    min_diff = float('inf')
    for value in lst:
        if value > target:
            diff = value - target
            if diff < min_diff:
                above_closest = value
                min_diff = diff

    index = lst.index(above_closest)
    return index

def below_closest_value(lst, target):
    print("HERE IN BELOW LOGIFC")
    small_l = []
    for i in lst:
        if i < target:
            small_l.append(i)
    max_val = max(small_l)
    return lst.index(max_val)

def closest_value(input_list, input_value):
    arr = np.asarray(input_list)
    i = (np.abs(arr - input_value)).argmin()
    index = input_list.index(arr[i])
    return index

from datetime import datetime
import datetime as dt
import pandas as pd
import math

def get_inst(selected_instrument, expiry_date):

    ticker          = [str(selected_instrument)]             # Stock name or (NIFTY, BANKNIFTY, FINNIFTY)
    expiry_date     = [str(expiry_date)]            # Enter Valid expiry Date
    column_filter   = "tradingsymbol"        #You can change it to "instrumenttoken" as well.
 

    expiry                          = [datetime.strptime(expiry_date[0], "%Y-%m-%d").date()]
    master_instruments_url          = 'https://api.kite.trade/instruments'
    ticker_df                       = pd.DataFrame()
    master_instruments_df           = pd.read_csv(master_instruments_url)
    master_instruments_df['expiry'] = pd.to_datetime(master_instruments_df['expiry'], format='%Y-%m-%d')
    df1 = master_instruments_df[
        (master_instruments_df["exchange"]  == "NFO")
        & (master_instruments_df["segment"] == "NFO-OPT")
        & (master_instruments_df["name"].isin(ticker))
        & (master_instruments_df["expiry"].isin(expiry_date))
    ][column_filter]
    instrument_list = df1.to_list()
    symbol_token_list = list(map(lambda i: "NFO:" + i, instrument_list))
    # pe_list = []
    # ce_list = []
    # for i in symbol_token_list:
    #     ce_or_pe = i[-2:]

    #     if ce_or_pe == "PE":
    #         pe_list.append(i)
    #     else:
    #         ce_list.append(i)
    return (symbol_token_list)

def get_inst_ce_pe(selected_instrument, expiry_date):
    ticker          = [str(selected_instrument)]             # Stock name or (NIFTY, BANKNIFTY, FINNIFTY)
    expiry_date     = [str(expiry_date)]            # Enter Valid expiry Date
    column_filter   = "tradingsymbol"        #You can change it to "instrumenttoken" as well.


    expiry                          = [datetime.strptime(expiry_date[0], "%Y-%m-%d").date()]
    master_instruments_url          = 'https://api.kite.trade/instruments'
    ticker_df                       = pd.DataFrame()
    master_instruments_df           = pd.read_csv(master_instruments_url)
    master_instruments_df['expiry'] = pd.to_datetime(master_instruments_df['expiry'], format='%Y-%m-%d')
    df1 = master_instruments_df[
        (master_instruments_df["exchange"]  == "NFO")
        & (master_instruments_df["segment"] == "NFO-OPT")
        & (master_instruments_df["name"].isin(ticker))
        & (master_instruments_df["expiry"].isin(expiry_date))
    ][column_filter]
    instrument_list = df1.to_list()
    symbol_token_list = list(map(lambda i: "NFO:" + i, instrument_list))
    pe_list = []
    ce_list = []
    for i in symbol_token_list:
        ce_or_pe = i[-2:]

        if ce_or_pe == "PE":
            pe_list.append(i)
        else:
            ce_list.append(i)

    # print(ce_list,pe_list)
    return (ce_list,pe_list)

# print(get_inst_ce_pe("BANKNIFTY","2023-05-11"))