#coding=utf-8
from selenium import webdriver
from pyvirtualdisplay import Display
import time

def search(fpdm,fphm):
    display = Display(visible=0, size=(1440, 900))
    display.start()
    driver = webdriver.Chrome()
    driver.get('http://wsbs.sc-n-tax.gov.cn/fpcy/init.htm')
    #driver.switch_to_frame('content')                  #因为表单在iframe里，所以需要先切换到iframe

    element = driver.find_element_by_xpath('//*[@id="fpdm"]')
    element.send_keys(fpdm)
    element = driver.find_element_by_xpath('//*[@id="fphm"]')
    element.send_keys(fphm)




    element = driver.find_element_by_xpath('//*[@id="submitBtn"]')
    element.click()
    time.sleep(2)
    driver.save_screenshot('static/result.png')
    driver.quit()
    display.stop()
