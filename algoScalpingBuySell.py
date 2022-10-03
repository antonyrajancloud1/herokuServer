import kite as kite
import requests
from dateutil.rrule import rrule, WEEKLY, TH
from flask import *
import datetime;

from kiteconnect import KiteConnect

import acctkn
from kite_trade import KiteApp

att = acctkn.att()
ap = acctkn.atp()
app = Flask(__name__)
# kite = KiteConnect(api_key=ap)
enctoken = "4ckGfr/jl4HCNmZl+vhrnOkVTWQYsJh6TGxpy6vFTn+bfIeCqJ/UE/0zfeb1UdgsW6ElkMftCxEODz+tNH86f5zgmt08V99GxQ/WGv8ioDOF/sg/poneBw=="
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
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=" + index_global
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8'}
    global option_data
    option_data = requests.get(url, headers=headers).json()
    return getExpiryList()


def getExpiryList():
    if option_data != "":
        expiry_dates = option_data["records"]["expiryDates"]
        global current_expiry
        current_expiry = expiry_dates[0]
        print(current_expiry)
        next_expiry = expiry_dates[1]

        if (str(current_expiry).split("-")[1] != (str(next_expiry).split("-")[1])):
            global is_monthly_expiry
            is_monthly_expiry = True
        # print(current_expiry)
        return current_expiry


def getExistingOrders():
    print("Existing Orders")
    return kite.positions()


def placeCallOption():
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

def placePutOption():
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


def exitOrder():
    if currentPremiumPlaced != "":
        print(currentPremiumPlaced)
        order_id = kite.place_order(tradingsymbol=currentPremiumPlaced, variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NFO,
                                    transaction_type=kite.TRANSACTION_TYPE_SELL, quantity=qty,
                                    order_type=kite.ORDER_TYPE_MARKET, product=kite.PRODUCT_MIS)
        print(order_id)
        print(currentPremiumPlaced + "exit order")
        getLTPForOption("exit")


def getCurrentAtm():
    niftyLTP = (kite.ltp(tradingsymbol)).get(tradingsymbol).get('last_price')
    print(niftyLTP)
    niftySpot = 50 * round(niftyLTP / 50)
    print(niftySpot)
    return niftySpot


def getTradingSymbol():
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


# print(getnsedata())
# print(is_monthly_expiry)
# print(getTradingSymbol()+str(getCurrentAtm())+"CE")
# print(is_monthly_expiry)
# getCurrentAtm()
def getLTPForOption(action):
    if currentPremiumPlaced != "":
        print("__________")
        ltp_str = json.dumps(kite.quote("NFO:" + currentPremiumPlaced))
        ltp = json.loads(ltp_str)["NFO:" + currentPremiumPlaced]["last_price"]
        print()
        with open('tradebook.txt', 'a') as file:
            file.write(
                currentPremiumPlaced + " \t " + action + " \t" + str(ltp) + "\t" + str(datetime.datetime.now()) + "\n")
        file.close()
        print("__________")


def checkIfOrderExists():
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


checkIfOrderExists()


@app.route('/')
def index():
    return render_template('html/algoscalping.html')
    #return render_template("Hi")

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
    app.run(ssl_context='adhoc')
