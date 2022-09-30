# This is a sample Python script.
import json


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


abc = {'net': [
    {'tradingsymbol': 'NIFTY22SEP16950PE', 'exchange': 'NFO', 'instrument_token': 18202114, 'product': 'NRML',
     'quantity': 100, 'overnight_quantity': 0, 'multiplier': 1, 'average_price': 0, 'close_price': 0,
     'last_price': 131.7, 'value': 117.5, 'pnl': 117.5, 'm2m': 117.5, 'unrealised': 117.5, 'realised': 0,
     'buy_quantity': 100, 'buy_price': 56.825, 'buy_value': 5682.5, 'buy_m2m': 5682.5, 'sell_quantity': 100,
     'sell_price': 58, 'sell_value': 5800, 'sell_m2m': 5800, 'day_buy_quantity': 100, 'day_buy_price': 56.825,
     'day_buy_value': 5682.5, 'day_sell_quantity': 100, 'day_sell_price': 58, 'day_sell_value': 5800}], 'day': [
    {'tradingsymbol': 'NIFTY22SEP16950PE', 'exchange': 'NFO', 'instrument_token': 18202114, 'product': 'NRML',
     'quantity': 150, 'overnight_quantity': 0, 'multiplier': 1, 'average_price': 0, 'close_price': 0,
     'last_price': 131.7, 'value': 117.5, 'pnl': 117.5, 'm2m': 117.5, 'unrealised': 117.5, 'realised': 0,
     'buy_quantity': 100, 'buy_price': 56.825, 'buy_value': 5682.5, 'buy_m2m': 5682.5, 'sell_quantity': 100,
     'sell_price': 58, 'sell_value': 5800, 'sell_m2m': 5800, 'day_buy_quantity': 100, 'day_buy_price': 56.825,
     'day_buy_value': 5682.5, 'day_sell_quantity': 100, 'day_sell_price': 58, 'day_sell_value': 5800}]}
currentPremiumPlaced = "NIFTY22SEP16950PE"
position_string = json.dumps(abc)
print(position_string)
position_json = json.loads(position_string)
print(type(position_json))
allDayPositions = position_json['day']
for position in allDayPositions:
    print(position['tradingsymbol'])
    if position['tradingsymbol'] == currentPremiumPlaced:
        if position['quantity'] >= 0:
            print(position['last_price'])
    print()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
