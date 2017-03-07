from __future__ import absolute_import, print_function
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def test_loginpage(live_server, env_browser):
       user = ""
       pwd = ""
       env_browser.get("https://zenodo.org/")
       elem = env_browser.find_element_by_id("email")
       elem.send_keys(user)
       elem = env_browser.find_element_by_id("pass")
       elem.send_keys(pwd)
       elem.send_keys(Keys.RETURN)
       env_browser.close()
