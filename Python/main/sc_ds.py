#coding=utf-8
from selenium import webdriver
from PIL import Image
import time

def get_captcha(driver):                      # 获取验证码图片
    driver.get('http://182.151.197.163:7002/FPCY_SCDS_WW/fpcy.jsp')
    driver.save_screenshot('yzm.png')  # saves screenshot of entire page
    im = Image.open('yzm.png')  # uses PIL library to open image in memory
    left = 557;
    top = 161;
    right = 645;
    bottom = 188
    im = im.crop((left, top, right, bottom))  # defines crop points
    im.save('yzm.png')  # saves new cropped image

def get_result(driver,fpdm,fphm,mima,yzm):
    #driver.switch_to_frame('content')                  #因为表单在iframe里，所以需要先切换到iframe
    element = driver.find_element_by_xpath("//*[@id='wwcytable']/tbody/tr[2]/td[2]/input")
    element.send_keys(fpdm)
    element = driver.find_element_by_xpath("//*[@id='wwcytable']/tbody/tr[3]/td[2]/input")
    element.send_keys(fphm)
    element = driver.find_element_by_xpath("//*[@id='wwcytable']/tbody/tr[4]/td[2]/input")
    element.send_keys(mima)

    #yzm=raw_input()
    element = driver.find_element_by_xpath('//*[@id="imgcode"]')
    element.send_keys(yzm)

    element = driver.find_element_by_xpath('//*[@id="wwcytable"]/tbody/tr[6]/td/input[1]')
    element.click()

    driver.save_screenshot('result.png')

