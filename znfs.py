#!/usr/bin/env python3
import configparser
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from time import sleep
import pickle
import logging

config = configparser.ConfigParser()
log_name = "LOG"
logging.basicConfig(filename=log_name,
                    filemode='a',
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

logging.info("Running Script")

log = logging.getLogger()

config['CREDS'] = {'email' : "replacemewith@email.com",
                  'passwd' : "replacemewithyourpsas"}
config_file_name = "config.cfg"
try:
    config.read_file(open(config_file_name))
except FileNotFoundError:
    with open(config_file_name, 'w') as f:
        config.write(f)


# Global Vars.
driver = webdriver.Chrome()
email = config['CREDS']['email']
passwd = config['CREDS']['passwd']
liked_pages = []
try:
    with open("cached_data.dat", "rb") as f:
        scraping_index, liked_pages = pickle.load(f)
except FileNotFoundError:
    scraping_index = 1

def login(email_arg, passwd_arg):
    driver.get("https://mbasic.facebook.com/")
    email = driver.find_element(By.NAME, "email")
    passwd = driver.find_element(By.NAME, "pass")
    login_btn = driver.find_element(By.NAME, "login")
    email.send_keys(email_arg)
    passwd.send_keys(passwd_arg)
    login_btn.click()

def scrape_liked_pages():
    global scraping_index
    driver.get(f"https://mbasic.facebook.com/yusufthehegazy?startindex={scraping_index}&v=likes&sectionid=9999")
    no_of_divs = len(driver.find_elements(By.TAG_NAME, "div"))
    initial_no_of_divs = no_of_divs
    try:
        while(no_of_divs == initial_no_of_divs):
            driver.get(f"https://mbasic.facebook.com/yusufthehegazy?startindex={scraping_index}&v=likes&sectionid=9999")
            no_of_divs = len(driver.find_elements(By.TAG_NAME, "div"))
            pages_links = [page.get_attribute('href') for page in driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]').find_elements_by_xpath('.//a')]
            pages_links.pop(0)
            pages_links.pop()
            pages_links.pop()
            liked_pages.extend(pages_links)
            scraping_index += 11
            pickle.dump((scraping_index, liked_pages), open("cached_data.dat", "wb"))
            log.info(f"Scrapping, Index: {scraping_index}, Links Scrapped: {len(liked_pages)}")
    except NoSuchElementException:
        if ("Blocked" in driver.page_source):
            log.info(f"Temporary blocked, sleeping for 15 mins...")
            sleep(60*15)
            scrape_liked_pages()

def unlike_page(page_id):
    driver.get(f"https://mbasic.facebook.com/{page_id}")
    unlike_btn = driver.find_element_by_link_text("Unlike")
    unlike_btn.click()

login(email, passwd)
scrape_liked_pages()
