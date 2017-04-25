#coding=utf-8
from selenium import webdriver
import time

driver = webdriver.Chrome()
driver.get('http://wsbs.sc-n-tax.gov.cn/fpcy/init.htm')


fpdm=151011676010

fphm="03221158"


#driver.switch_to_frame('content')                  #因为表单在iframe里，所以需要先切换到iframe

element = driver.find_element_by_xpath('//*[@id="fpdm"]')
element.send_keys(fpdm)
element = driver.find_element_by_xpath('//*[@id="fphm"]')
element.send_keys(fphm)




element = driver.find_element_by_xpath('//*[@id="submitBtn"]')
element.click()
time.sleep(2)
driver.save_screenshot('result.png')
