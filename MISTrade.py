import kite as kite
import os
from flask import *
import datetime;
import acctkn
from kite_trade import KiteApp

att = acctkn.att()
ap = acctkn.atp()
app = Flask(__name__)
# kite = KiteConnect(api_key=ap)
apiToken = os.getenv("APITOKEN")
targetPoints=os.getenv("TARGET")
lots = os.getenv("LOTS")
STOCKNAME = os.getenv("STOCKNAME")
kite = KiteApp(enctoken=apiToken)

isTradeAllowed= True
qty = int(lots)
currentPremiumPlaced = ""
currentOrderID = ""
print("lots")
print(lots)
print(STOCKNAME)
print("++++++++")

def getExistingOrders():
    try:
        print("Existing Orders")
        print(kite.orders())
        return kite.orders()
    except BaseException as e:
        print("exception in getExistingOrders  -----  " + str(e))


def placeCallOption():
    try:
        if isTradeAllowed:
            order_id = kite.place_order(tradingsymbol=STOCKNAME, variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NSE,
                                        transaction_type=kite.TRANSACTION_TYPE_BUY, quantity=qty,
                                        order_type=kite.ORDER_TYPE_MARKET, product=kite.PRODUCT_MIS)
            if order_id["status"] == "success":
                global currentOrderID
                currentOrderID = "BUY"
                getLTPForOption("BUY")
                print("Buy Success")
            else:
                print(order_id)
        else:
            print("Traing is blocked in server")
    except BaseException as e:
        print("exception in placeCallOption ---- " + str(e))


def placePutOption():
    try:
        if isTradeAllowed:
            order_id = kite.place_order(tradingsymbol=STOCKNAME, variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NSE,
                                        transaction_type=kite.TRANSACTION_TYPE_SELL, quantity=qty,
                                        order_type=kite.ORDER_TYPE_MARKET, product=kite.PRODUCT_MIS)
            if order_id["status"] == "success":
                global currentOrderID
                currentOrderID = "SELL"
                getLTPForOption("SELL")
                print("Sell Success")

            else:
                print(order_id)
        else:
            print("Traing is blocked in server")
    except BaseException as e:
        print("exception in placeCallOption ---- " + str(e))


def getLTPForOption(action):
    try:
        print("__________")
        ltp_str = json.dumps(kite.quote("NFO:" + STOCKNAME))
        ltp = json.loads(ltp_str)["NFO:" + STOCKNAME]["last_price"]
        print("tradebooklogs = " + STOCKNAME + " \t " + action + " \t" + str(ltp) + "\t" + str(
            datetime.datetime.now()) + "\n")
        print("__________")
        return ltp
    except BaseException as e:
        print("exception in getLTPForOption  -----  " + str(e))

@app.route('/')
def index():
    return render_template('html/algoscalping.html')

@app.route('/buy', methods=["GET", "POST"])
def buyCE():
    print("Entry CE")
    if currentOrderID == "":
        placeCallOption()
    else:
        placeCallOption()
        placeCallOption()
    return render_template('html/algoscalping.html', option=currentPremiumPlaced + "Order placed")


@app.route('/sell', methods=["GET", "POST"])
def buyPE():
    print("Entry PE")
    if currentOrderID =="":
        placePutOption()
    else:
        placePutOption()
        placePutOption()
    return render_template('html/algoscalping.html', option=currentPremiumPlaced + " Order placed")
@app.route('/exit', methods=["GET", "POST"])
def exit():
    if currentOrderID=="BUY":
        placePutOption()
    elif currentOrderID=="SELL":
        placeCallOption()
    else:
        print("check currentOrderID = "+currentOrderID)
    return render_template('html/algoscalping.html', option=currentPremiumPlaced + " Order placed")
@app.route('/settoggle/<message>', methods=["GET", "POST"])
def setToggle(message):
    print("Set toggle")
    global isTradeAllowed
    if message=="false":
        isTradeAllowed=False
    elif message=="true":
        isTradeAllowed=True
    print(isTradeAllowed)
    return render_template('html/algoscalping.html', option=isTradeAllowed)

@app.route('/getvalues', methods=["GET", "POST"])
def getvalues():
    allValues={"currentPremiumPlaced":STOCKNAME,"lots":lots,"targetPoints":targetPoints}
    return allValues

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
