import time
import pychrome as pychrome
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# UpdateCredentials
Emailid = "antonyrajan.d@zohocorp.com"
Password = "Antony123"
ClientID = "1000.1JRZE8QOCUHSJ2U40EYHVPSTFPUPEG"
ClientSecret = "7bcd1a30803ae656c25764de2d7c1fe78b2eb66cf1"

oauthurl = "https://accounts.csez.zohocorpin.com/oauth/v2/auth?scope=SDPOnDemand.assets.all,SDPOnDemand.setup.all,SDPOnDemand.requests.all,SDPOnDemand.purchases.all,SDPOnDemand.changes.all,SDPOnDemand.projects.all,SDPOnDemand.solutions.all,SDPOnDemand.cmdb.all&client_id=" + ClientID + "&state=test&response_type=code&redirect_uri=https://www.getpostman.com/oauth2/callback&access_type=offline&prompt=consent"
codes = []
finalCode = ""


def output_on_start(**kwargs):
    for key in kwargs:
        if key.__contains__("documentURL"):
            Networkurl = kwargs["documentURL"]
            Networkurl = str(Networkurl)
            if Networkurl.__contains__("test&code"):
                code = Networkurl.split("test&code=")
                code = code[1].split("&")
                global finalCode
                finalCode = code[0]
                # print(finalCode)


def output_on_end(**kwargs):
    if kwargs.__contains__("documentURL"):
        print(kwargs["documentURL"])


def printNetwork():
    tab.call_method("Network.emulateNetworkConditions", offline=False, latency=100, downloadThroughput=93750,
                    uploadThroughput=31250, connectionType="cellular3g")
    tab.call_method("Network.enable", _timeout=20)
    tab.set_listener("Network.requestWillBeSent", output_on_start)
    tab.set_listener("Network.responseReceived", output_on_end)


def login():
    time.sleep(3)
    driver.find_element(By.ID, "login_id").send_keys(Emailid + Keys.ENTER)
    time.sleep(2)
    driver.find_element(By.ID, "password").send_keys(Password + Keys.ENTER)


chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--remote-debugging-port=8001")
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
dev_tools = pychrome.Browser(url="http://localhost:8001")
tab = dev_tools.list_tab()[0]

tab.start()
start = time.time()
driver.get("https://accounts.csez.zohocorpin.com/")
print(int(time.time() - start))
printNetwork()
start = time.time()
driver.get("https://accounts.csez.zohocorpin.com/")
print(int(time.time() - start))
login()
time.sleep(3)
driver.get(oauthurl)
time.sleep(1)
driver.find_element(By.CLASS_NAME, "btn").click()
postAuthURL = "https://accounts.csez.zohocorpin.com/oauth/v2/token?code=" + finalCode + "&client_id=" + ClientID + "&client_secret=" + ClientSecret + "&redirect_uri=https://www.getpostman.com/oauth2/callback&grant_type=authorization_code"
# print(postAuthURL)
r = requests.post(postAuthURL)
print(r.content)
tokens = r.json()
refresh_token = tokens["refresh_token"]
refreshUrl = "https://accounts.csez.zohocorpin.com/oauth/v2/token?refresh_token=" + refresh_token + "&client_id=" + ClientID + "&client_secret=" + ClientSecret + "&redirect_uri=https://www.getpostman.com/oauth2/callback&grant_type=refresh_token"
print(refreshUrl)
