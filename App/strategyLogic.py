import datetime as dt
from time import sleep
import sys
from pya3 import *
from .common_functionsV2 import generate_session, check_margin, get_order_status, get_oid, ap_generator, latest_expiry,monthly_expiry, modify_ce_order_to_cost,modify_pe_order_to_cost, get_ltp_info, below_closest_value, above_closest_value, closest_value, get_inst_ce_pe
from .send_message import send_email, send_msg
from sys import exit
import pymongo
from pymongo import MongoClient

days_to_jump = 1
# symbol = "Nifty 50"


#________________________________
# if entryType == "LPH":
#     stop_loss = "LPH Stoploss"
# else:
#     stop_loss = "LPL Stoploss"


client = pymongo.MongoClient("mongodb+srv://aayush_gp:3yYfnXZVJZHvdu98@internal.ilq0ndz.mongodb.net/?retryWrites=true&w=majority")
db = client['lowHighTrends']
user_collection = db['userCredentials']
doc_id = "LPL_LPH_USER_CREDS"
filter_query = {'_id': doc_id}
userData = dict(user_collection.find_one(filter_query))


client_code = "TESTCLIENT"
username = userData['userId']
api_key = userData['api_key']
print("RUNNING STRATEGY FOR USER ::",username)
strategy = "NIFTY LPH/LPL STRATEGY"



alice = Aliceblue(user_id=username,api_key=api_key)
print(alice.get_session_id())





LTP = 0
socket_opened = False
subscribe_flag = False
subscribe_list = []
unsubscribe_list = []

def socket_open():
    print("Connected")
    global socket_opened
    socket_opened = True
    if subscribe_flag: 
        alice.subscribe(subscribe_list)

def socket_close():
    global socket_opened, LTP
    socket_opened = False
    LTP = 0
    print("Closed")

def socket_error(message): 
    global LTP
    LTP = 0
    print("Error :", message)

def feed_data(message): 
    global LTP, subscribe_flag
    feed_message = json.loads(message)
    
    if feed_message["t"] == "ck":
        subscribe_flag = True
        pass
    elif feed_message["t"] == "tk":
        pass
    else:
        LTP = feed_message[
            'lp'] if 'lp' in feed_message else LTP 
        print(LTP)


def main():
    global alice,socket_opened,username,password,twoFA,api_secret,order_placed,quantity,script,expiry_days,days_to_jump,nf_script
    global expiry_type, instrument_to_trade, strategyData,symbol, triggerLevel, entryType, stoploss, lots, strategyStatus, stoplossStatus, stop_loss

    strategyData = (collection.find_one(query))

    strategyStatus = strategyData['strategyStatus']
    stoplossStatus = strategyData['stoplossStatus']
    symbol = strategyData['instrument']
    lots = int(strategyData['lots'])
    triggerLevel = float(strategyData['triggerLevel'])



    

    if strategyStatus == "INACTIVE":
        msg = "STRATEGY STATUS IS INACTIVE SO WE WILL EXIT!"
        print(msg)
        send_msg(msg)
        exit()
    else:
        print("STRATEGY STATUS ACTIVE, STARTING...")
        
     
    if stoplossStatus == "INACTIVE":
        print("Stoploss status is Inactive!")


        alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)
        while not socket_opened:
            pass

        instrument = alice.get_instrument_by_symbol('NSE',symbol)
        subscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
        alice.subscribe(subscribe_list)
        
        expiry_type = "monthly_expiry"
        assigning_variables(symbol)
        quantity = lot_size * lots
        order_placed = False

        instrument_to_trade = alice.get_instrument_for_fno(exch="NFO", symbol =  trading_symbol,expiry_date=str(expiry_date), is_fut=True,strike=None,is_CE = False)
        print(instrument_to_trade)
        
        if getStatusAndEntrytype("ENTRYTYPE") == "LPH":
            while float(LTP) < triggerLevel:

                strategyData = (collection.find_one(query))
                symbol = strategyData['instrument']
                triggerLevel = float(strategyData['triggerLevel'])
                entryType = strategyData['entryType']
                stoploss =float(strategyData['stoploss'])
                lots = int(strategyData['lots'])
                stop_loss = "LPH Stoploss"

                if dt.datetime.now().time() > dt.time(15,29,30):
                    exit()
                print("waiting for LPH break, LPH LEVEL-->",triggerLevel)
                sleep(2)
            buy_future()
            entryType = "TAKEN_LPH"
            stoploss_value_LPH = int(triggerLevel - (triggerLevel * stoploss /100) )
            updateData("stoploss_value_LPH",stoploss_value_LPH)
            status = "entryType Taken in LPH"
            print("STATUS :::",status)
            print("ENTY TYPOE :::",entryType)
            print("stoploss_value_LPH :::",stoploss_value_LPH)
            updateStatusAndEntrytype(status,entryType)
            updateData("stoplossStatus","ACTIVE")
            check_LPH_stoploss()
            

        elif getStatusAndEntrytype("ENTRYTYPE") == "LPL":

            while float(LTP) > triggerLevel:

                strategyData = (collection.find_one(query))
                symbol = strategyData['instrument']
                triggerLevel = float(strategyData['triggerLevel'])
                entryType = strategyData['entryType']
                stoploss =float(strategyData['stoploss'])
                lots = int(strategyData['lots'])
                stop_loss = "LPH Stoploss"

                if dt.datetime.now().time() > dt.time(15,29,30):
                    exit()
                print("waiting for LPL break")
                sleep(2)
            sell_future()
            stoploss_value_LPL = int(triggerLevel + (triggerLevel * stoploss /100) )
            updateData("stoploss_value_LPL",stoploss_value_LPL)
            entryType = "TAKEN_LPL"
            status = "Entry Taken in LPL"
            updateStatusAndEntrytype(status,entryType)
            updateData("stoplossStatus","ACTIVE")
            check_LPL_stoploss()
            
        print("CHECKING IFs entryType is ",entryType)

    else: 
        alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)
        while not socket_opened:
            pass

        instrument = alice.get_instrument_by_symbol('NSE',symbol)
        subscribe_list = [alice.get_instrument_by_symbol('INDICES',symbol)]
        alice.subscribe(subscribe_list)
        
        expiry_type = "monthly_expiry"
        assigning_variables(symbol)
        quantity = lot_size * lots
        order_placed = False

        instrument_to_trade = alice.get_instrument_for_fno(exch="NFO", symbol =  trading_symbol,expiry_date=str(expiry_date), is_fut=True,strike=None,is_CE = False)
        print(instrument_to_trade)
        
        check_LPH_stoploss()
        check_LPL_stoploss()



def check_LPH_stoploss():
    if getStatusAndEntrytype("ENTRYTYPE") == "TAKEN_LPH":
        print("IN SL LPH LOGIC !!!!!!!!!!!")
        while float(LTP) > getData("stoploss_value_LPH"):
            if dt.datetime.now().time() > dt.time(15,29,30):
                exit()
            print("wait for LPH stoploss trigger")
            sleep(2)
        sell_future("STOPLOSS REQUEST")
        updateData("strategyStatus","INACTIVE")
        updateData("status","LPH STOPLOSS HIT")




def check_LPL_stoploss():
    if getStatusAndEntrytype("ENTRYTYPE") == "TAKEN_LPL":
        while float(LTP) < getData("stoploss_value_LPL"):
            if dt.datetime.now().time() > dt.time(15,29,30):
                exit()
            print("wait for LPL stoploss trigger")
            sleep(2)
        buy_future("STOPLOSS REQUEST")
        updateData("strategyStatus","INACTIVE")
        updateData("status","LPL STOPLOSS HIT")



def buy_future(requestType = None):

    try:
        buy_future = alice.place_order(transaction_type=TransactionType.Buy,instrument=instrument_to_trade,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Delivery,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
        sleep(2)
        oid_buy_future = buy_future['NOrdNo']
        if get_order_status(alice,oid_buy_future) != 'complete':
            msg = "Future Buy is Complete. Strategy- "+strategy
            send_msg(msg)
        else:
            order_status = get_order_status(alice,oid_buy_future)
            msg = "Issue with future order: Order Status is " + order_status +" in strategy "+ strategy
            send_msg(msg)

    except Exception as e:
        print(f"some error occured at intial main:::>{e}")
        error = f"{e}"
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("An error ocurred at Line number: ", line_number)
        msg = "Some error occurred in "+strategy+" in line number "+str(line_number)+" with error as "+error
        send_msg(msg)
        print('msg sent')
        exit()

    if requestType != None:
        updateData("stoplossStatus","INACTIVE")


def sell_future(requestType = None):
    try:
        sell_future = alice.place_order(transaction_type=TransactionType.Sell,instrument=instrument_to_trade,quantity=quantity,order_type=OrderType.Market,product_type = ProductType.Delivery,price = 0.0,trigger_price=None,stop_loss=None,square_off=None,trailing_sl=None,is_amo=False)
        sleep(2)
        oid_sell_future = sell_future['NOrdNo']
        if get_order_status(alice,oid_sell_future) != 'complete':
            msg = "Future Buy is Complete. Strategy- "+strategy
            send_msg(msg)
        else:
            order_status = get_order_status(alice,oid_sell_future)
            msg = "Issue with future order: Order Status is " + order_status +" in strategy "+ strategy
            send_msg(msg)

    except Exception as e:
        print(f"some error occured at intial main:::>{e}")
        error = f"{e}"
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("An error ocurred at Line number: ", line_number)
        msg = "Some error occurred in LPL LPH SERVER" +"in line number "+str(line_number)+" with error as "+error
        send_msg(msg)
        print('msg sent')
        exit()

    if requestType != None:
        updateData("stoplossStatus","INACTIVE")

def assigning_variables(symbol):
    global trading_symbol,strike_range,q,expiry_date,ttype,slttype,tgtttype,quantity, lot_size

    if symbol =='NIFTY BANK':
        trading_symbol = 'BANKNIFTY'

    if symbol =='NIFTY 50':
        trading_symbol = 'NIFTY'

    if symbol =='NIFTY FIN SERVICE':
        trading_symbol = 'FINNIFTY'

    if trading_symbol =='BANKNIFTY':
        strike_range = 100
        lot_size = 25

    elif trading_symbol =='NIFTY':
        strike_range = 50
        lot_size = 50

    elif trading_symbol =='FINNIFTY':
        strike_range = 50
        lot_size = 50

    if expiry_type == "Week":
        expiry_date =str(latest_expiry(trading_symbol))
    else:
        expiry_date =str(monthly_expiry(trading_symbol))
    print("EXPIRY DATE-->",expiry_date)

def updateStatusAndEntrytype(status,entryType):
    filter_query = {'_id': doc_id}
    update_query = {'$set': {
        'status': status,
        'entryType':entryType                    
                            }}
    result = collection.update_one(filter_query, update_query)

def updateData(field,value):
    filter_query = {'_id': doc_id}
    update_query = {'$set': {field: value}}
    result = collection.update_one(filter_query, update_query)

def getData(field):
    query = {'_id': doc_id}
    docData = (collection.find_one(query))
    return docData[field]
    
def checkImmediateStop():
    query = {'_id': doc_id}
    docData = (collection.find_one(query))
    immediateStop = docData['immediateStop']
    if immediateStop == True:
        print("WE GOT AN IMMEDIATE STOP REQUEST, CLOSING THE SCRIPT!")
        sys.exit()

def getStatusAndEntrytype(request):
    query = {'_id': doc_id}
    docData = (collection.find_one(query))
    
    if request == "STATUS":
        status = docData['status']
        return status
    else:
        entryType = docData['entryType']
        return entryType


    
client = pymongo.MongoClient("mongodb+srv://aaush:AaushMongoTestAccount@gopassive.niccs6s.mongodb.net/?retryWrites=true&w=majority")
db = client['lowHighTrends']
collection = db['inputData']

doc_id= "NIFTY_LPL_LPH_DETAILS"
query = {'_id': doc_id}


if (__name__=='__main__'):
    print('start')
    main()

