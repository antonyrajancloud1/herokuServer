import kite as kite
import os
import requests
from dateutil.rrule import rrule, WEEKLY, TH
from flask import *
import datetime;
import pandas as pd


from kiteconnect import KiteConnect

import acctkn
from kite_trade import KiteApp

att = acctkn.att()
ap = acctkn.atp()
app = Flask(__name__)
# kite = KiteConnect(api_key=ap)
enctoken = "+CfEOkwRZlPGQnIXiSDouvcoF93qrBU6Q1nfvnH7R+64iPbQZTIP5Nl6dqHlFIU+dAWcPZbgq04DlI4yWhJNJoI5aANB4GHDsYtYt10mUCCDlwAhhWM1Lw=="
kite = KiteApp(enctoken=enctoken)
# kite.set_access_token(att)
option_data = {}
current_expiry = ""
index_global = "NIFTY"
is_monthly_expiry = False
tradingsymbol = 'NSE:NIFTY 50'
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
        #url = "https://www.nseindia.com/api/option-chain-indices?symbol=" + index_global
        #headers = {
        #    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        #    'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8'}
        #print(url)
        global option_data
        #option_data = kite.http_get(url,headers)
        #print(option_data)
        df = pd.DataFrame(kite.instruments())
        print(df)
        df = df[(df.name == index_global)]
        df = sorted(df.expiry.unique())
        print(df)
        option_data[0]=str( datetime.datetime.strptime(str(df[0]), '%Y-%m-%d').strftime('%d-%b-%Y'))
        option_data[1]=str( datetime.datetime.strptime(str(df[1]), '%Y-%m-%d').strftime('%d-%b-%Y'))
        #print(option_data)
        return getExpiryList()
    except BaseException as e:
        print("exception in getNseData  -----  " + str(e))


def getExpiryList():
    try:
        print(option_data)
        if option_data != "":
            #expiry_dates = option_data["records"]["expiryDates"]
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


def placeCallOption():
    try:
        exitOrder()
        # niftySpot = getCurrentAtm()
        checkIfOrderExists()
        optionToBuy = getTradingSymbol() + str(getCurrentAtm()) + "CE"
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
        getLTPForOption("Buy")
    except BaseException as e:
        print("exception in placeCallOption ---- " + str(e))


def placePutOption():
    try:
        exitOrder()
        checkIfOrderExists()
        optionToBuy = getTradingSymbol() + str(getCurrentAtm()) + "PE"
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
        getLTPForOption("Buy")
    except BaseException as e:
        print("exception in placePutOption ----- " + str(e))


def exitOrder():
    try:
        if currentPremiumPlaced != "":
            print(currentPremiumPlaced)
            order_id = kite.place_order(tradingsymbol=currentPremiumPlaced, variety=kite.VARIETY_REGULAR,
                                        exchange=kite.EXCHANGE_NFO,
                                        transaction_type=kite.TRANSACTION_TYPE_SELL, quantity=qty,
                                        order_type=kite.ORDER_TYPE_MARKET, product=kite.PRODUCT_MIS)
            print(order_id)
            print(currentPremiumPlaced + "exit order")
            getLTPForOption("exit")
    except BaseException as e:
        print("exception in exitOrder ---- " + str(e))


def getCurrentAtm():
    try:
        niftyLTP = (kite.ltp(tradingsymbol)).get(tradingsymbol).get('last_price')
        print(niftyLTP)
        niftySpot = 50 * round(niftyLTP / 50)
        print(niftySpot)
        return niftySpot
    except BaseException as e:
        print("exception in getCurrentAtm  -----  " + str(e))


def getTradingSymbol():
    try:
        getnsedata()
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
        if currentPremiumPlaced != "":
            print("__________")
            ltp_str = json.dumps(kite.quote("NFO:" + currentPremiumPlaced))
            ltp = json.loads(ltp_str)["NFO:" + currentPremiumPlaced]["last_price"]
            print()
            with open('tradebook.txt', 'a') as file:
                file.write(
                    currentPremiumPlaced + " \t " + action + " \t" + str(ltp) + "\t" + str(
                        datetime.datetime.now()) + "\n")
            file.close()
            print("__________")
    except BaseException as e:
        print("exception in getLTPForOption  -----  " + str(e))


def checkIfOrderExists():
    try:
        position_string = json.dumps(getExistingOrders())
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


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
