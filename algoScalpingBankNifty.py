import kite as kite
import os

import pytz
import requests
from dateutil.rrule import rrule, WEEKLY, TH
from flask import *
import datetime;
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

from kiteconnect import KiteConnect

import acctkn
from kite_trade import KiteApp

att = acctkn.att()
ap = acctkn.atp()
app = Flask(__name__)
# kite = KiteConnect(api_key=ap)
apiToken = os.getenv("APITOKEN")
kite = KiteApp(enctoken=apiToken)
# kite.set_access_token(att)
option_data = {}
current_expiry = ""
index_global = "BANKNIFTY"
is_monthly_expiry = False
tradingsymbol = 'NSE:NIFTY BANK'
lots = 10
qty = 50 * lots

currentPremiumPlaced = ""


# Basic calls
# print(kite.margins())
# print(kite.orders())
# print(kite.positions())
# print(kite.instruments("NFO"))
# kite.orders()

def getnsedata():
    try:
        global option_data
        df = pd.DataFrame(kite.instruments())
        print(df)
        df = df[(df.name == index_global)]
        df = sorted(df.expiry.unique())
        print(df)
        option_data[0] = str(datetime.datetime.strptime(str(df[0]), '%Y-%m-%d').strftime('%d-%b-%Y'))
        option_data[1] = str(datetime.datetime.strptime(str(df[1]), '%Y-%m-%d').strftime('%d-%b-%Y'))
        # print(option_data)
        # return getExpiryList()
    except BaseException as e:
        print("exception in getNseData Kite instruments  -----  " + str(e))


def getExpiryList():
    try:
        print(option_data)
        if option_data != "":
            # expiry_dates = option_data["records"]["expiryDates"]
            global current_expiry
            current_expiry = option_data[0]
            print(current_expiry)
            next_expiry = option_data[1]

            if (str(current_expiry).split("-")[1] != (str(next_expiry).split("-")[1])):
                global is_monthly_expiry
                is_monthly_expiry = True
            # print(current_expiry)
            return current_expiry
    except BaseException as e:
        print("exception in getExpiryList  -----  " + str(e))


def getExistingOrders():
    try:
        print("Existing Orders")
        return kite.positions()
    except BaseException as e:
        print("exception in getExistingOrders  -----  " + str(e))


def placeCallOption(message):
    try:
        exitOrder(message)
        # niftySpot = getCurrentAtm()
        checkIfOrderExists()
        optionToBuy = getTradingSymbol() + str(getCurrentAtm()-500) + "CE"
        print(optionToBuy)
        order_id = kite.place_order(tradingsymbol=optionToBuy, variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NFO,
                                    transaction_type=kite.TRANSACTION_TYPE_BUY, quantity=qty,
                                    order_type=kite.ORDER_TYPE_MARKET, product=kite.PRODUCT_MIS)
        if order_id["status"] == "success":
            if order_id["data"]["order_id"] != "":
                global currentPremiumPlaced
                currentPremiumPlaced = optionToBuy
        print(order_id)
        print(currentPremiumPlaced + "call Option")
        getLTPForOption("Buy  -- "+message)
    except BaseException as e:
        print("exception in placeCallOption ---- " + str(e))


def placePutOption(message):
    try:
        exitOrder(message)
        checkIfOrderExists()
        optionToBuy = getTradingSymbol() + str(getCurrentAtm()+500) + "PE"
        global currentPremiumPlaced
        currentPremiumPlaced = optionToBuy
        order_id = kite.place_order(tradingsymbol=optionToBuy, variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NFO,
                                    transaction_type=kite.TRANSACTION_TYPE_BUY, quantity=qty,
                                    order_type=kite.ORDER_TYPE_MARKET, product=kite.PRODUCT_MIS)
        if order_id["status"] == "success":
            if order_id["data"]["order_id"] != "":
                currentPremiumPlaced = optionToBuy
        print(order_id)
        print(currentPremiumPlaced + "Put Option")
        getLTPForOption("Buy  -- "+message)
    except BaseException as e:
        print("exception in placePutOption ----- " + str(e))


def exitOrder(message):
    try:
        if currentPremiumPlaced != "":
            print(currentPremiumPlaced)
            order_id = kite.place_order(tradingsymbol=currentPremiumPlaced, variety=kite.VARIETY_REGULAR,
                                        exchange=kite.EXCHANGE_NFO,
                                        transaction_type=kite.TRANSACTION_TYPE_SELL, quantity=qty,
                                        order_type=kite.ORDER_TYPE_MARKET, product=kite.PRODUCT_MIS)
            print(order_id)
            print(currentPremiumPlaced + "exit order")
            getLTPForOption("exit -- "+ message)
    except BaseException as e:
        print("exception in exitOrder ---- " + str(e))


def getCurrentAtm():
    try:
        print(kite.ltp(tradingsymbol))


        niftyLTP = (kite.ltp(tradingsymbol)).get(tradingsymbol).get('last_price')
        print(niftyLTP)
        niftySpot = 100 * round(niftyLTP / 100)
        print(niftySpot)
        return niftySpot
    except BaseException as e:
        print("exception in getCurrentAtm  -----  " + str(e))


def getTradingSymbol():
    try:
        # getnsedata()
        getExpiryList()
        global symbol
        today = datetime.date.today()
        year = str(today.year)[2:4]

        if is_monthly_expiry:
            month = str(current_expiry.split("-")[1]).upper()
            symbol = index_global + year + month
            print(symbol)
        else:
            month = str(current_expiry.split("-")[1]).upper()[0]
            next_thursday = rrule(freq=WEEKLY, dtstart=today, byweekday=TH, count=1)[0]
            date = str(next_thursday)[8:10]
            symbol = "" + index_global + year + month + date
            print(symbol)
        return symbol
    except BaseException as e:
        print("exception in getTradingSymbol  -----  " + str(e))


# print(getnsedata())
# print(is_monthly_expiry)
# print(getTradingSymbol()+str(getCurrentAtm())+"CE")
# print(is_monthly_expiry)
# getCurrentAtm()
def getLTPForOption(action):
    try:
        print("__________")
        ltp_str = json.dumps(kite.quote("NFO:" + currentPremiumPlaced))
        ltp = json.loads(ltp_str)["NFO:" + currentPremiumPlaced]["last_price"]
        print("tradebooklogs = " + currentPremiumPlaced + " \t " + action + " \t" + str(ltp) + "\t" + str(datetime.datetime.now()) + "\n")
        print("__________")
    except BaseException as e:
        print("exception in getLTPForOption  -----  " + str(e))


def checkIfOrderExists():
    try:
        existingOrderList = getExistingOrders()
        if existingOrderList is not None:
            position_string = json.dumps(existingOrderList)
            position_json = json.loads(position_string)
            allDayPositions = position_json['day']
            if allDayPositions != []:
                for position in allDayPositions:
                    print(position['tradingsymbol'])
                    if position['tradingsymbol'] == currentPremiumPlaced:
                        if position['quantity'] >= 0:
                            # print(position['last_price'])
                            exitOrder()
            else:
                print("No day positions")
        print()
    except BaseException as e:
        print("exception in checkIfOrderExists  -----  " + str(e))


# checkIfOrderExists()
@app.route('/')
def index():
    return render_template('html/algoscalping.html')
    # return render_template("Hi")


@app.route('/buy', methods=["GET", "POST"])
def buyCE():
    print("Entry CE")
    placeCallOption()
    return render_template('html/algoscalping.html', option=currentPremiumPlaced + "Order placed")


@app.route('/sell', methods=["GET", "POST"])
def buyPE():
    print("Entry PE")
    placePutOption()
    return render_template('html/algoscalping.html', option=currentPremiumPlaced + " Order placed")


@app.route('/exit', methods=["GET", "POST"])
def exitCurrentOrder():
    print("Exit Order")
    exitOrder()
    return render_template('html/algoscalping.html', option=currentPremiumPlaced + "Order Exited")


@app.route('/setexpiry', methods=["GET", "POST"])
def getExpiry():
    print("Expiry Called manually")
    getnsedata()
    return render_template('html/algoscalping.html', option="Expiry set" + "Order Exited")


#######################
@app.route('/buy/<message>', methods=["GET", "POST"])
def buyCE1(message):
    print("Entry CE")
    placeCallOption(message)
    return render_template('html/algoscalping.html', option=currentPremiumPlaced + "Order placed")


@app.route('/sell/<message>', methods=["GET", "POST"])
def buyPE1(message):
    print("Entry PE")
    placePutOption(message)
    return render_template('html/algoscalping.html', option=currentPremiumPlaced + " Order placed")


######################


scheduler = BackgroundScheduler(daemon=True, timezone=pytz.timezone('Asia/Calcutta'))
scheduler.add_job(getnsedata, 'cron', day_of_week='fri', hour=9, minute=3)
scheduler.start()
getnsedata()
#createDB()
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)


def getLTPForOption(action):
    try:
        print("__________")
        ltp_str = json.dumps(kite.quote("NFO:" + currentPremiumPlaced))
        ltp = json.loads(ltp_str)["NFO:" + currentPremiumPlaced]["last_price"]
        print()
        with open('tradebook.txt', 'a') as file:
            file.write(
                currentPremiumPlaced + " \t " + action + " \t" + str(ltp) + "\t" + str(datetime.datetime.now()) + "\n")
            file.close()
        print("tradebooklogs = " + currentPremiumPlaced + " \t " + action + " \t" + str(ltp) + "\t" + str(
            datetime.datetime.now()) + "\n")
        print("__________")
    except BaseException as e:
        print("exception in getLTPForOption  -----  " + str(e))
