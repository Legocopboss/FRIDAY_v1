import os
import random
import string
import time
import urllib
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *



code = str(os.getenv("SPOTIFY_CODE"))
state = ''.join(random.choices(string.ascii_letters, k=16))
scope = 'user-read-private user-read-email user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-read-playback-position user-top-read user-read-recently-played user-library-modify user-library-read'

url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode({
    'response_type': 'code',
    'client_id': str(os.getenv("SPOTIFY_CLIENT_ID")),
    'scope': scope,
    'redirect_uri': 'http://localhost',
    'state': state,
})

path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

PROXY = "localhost:9515"

options = Options()
options.binary_location = path
options.add_argument("user-data-dir=C:\\Users\\legoc\\AppData\\Local\\Google\\Chrome\\User Data")
options.add_argument("profile-directory=Profile 1")
options.add_argument("disable-dev-shm-usage")
options.add_argument("no-sandbox")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
webdriver.DesiredCapabilities.CHROME['acceptSslCerts'] = True
webdriver.DesiredCapabilities.CHROME['proxy'] = {
    'httpProxy': PROXY,
    'ftpProxy': PROXY,
    'sslProxy': PROXY,
    'proxyType': "MANUAL",
}

def oAuth():
    service = webdriver.ChromeService()
    service.path = "C:\chromedriver.exe"
    browser = webdriver.Chrome(options=options, service=service)
    try:
        browser.get(url)
    except WebDriverException as e:
        print(e.msg)
    time.sleep(1)
    os.environ["SPOTIFY_CODE"] = browser.current_url.split("?code=")[1].split("&state")[0]
    return browser.current_url.split("?code=")[1].split("&state")[0]

