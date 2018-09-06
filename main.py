# encoding: utf-8

import pandas as pd
import re
import pytesseract
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from pandas import DataFrame
from io import BytesIO
from PIL import Image
 
options = webdriver.ChromeOptions()
options.set_headless()
driver = webdriver.Chrome(chrome_options=options)
 
index = 0
index_1 = 0
frame_1 = DataFrame(columns=['区','街道','小区','房间数','房间朝向','房间网址',\
                             '面积','楼层','最近地铁距离','价格'])
box = (180,316,820,383)

def get_price(element):
	print(element)
	left = element.location['x']
	top = element.location['y']
	right = element.location['x'] + element.size['width']
	bottom = element.location['y'] + element.size['height']

	im = Image.open('screenshot.png') 
	im = im.crop((left, top, right, bottom))
	im.show()

	return 0
 
for url in ['http://www.ziroom.com/z/nl/z2.html?qwd=%E6%99%BA%E5%AD%A6%E8%8B%91']:
    driver.get(url)
    # 保存网页截图
    driver.save_screenshot('screenshot.png')
    locator_f = (By.ID,'page')
    WebDriverWait(driver,10,0.5).until(EC.presence_of_element_located(locator_f))
    locator = (By.ID,'houseList')
    WebDriverWait(driver,10,0.5).until(EC.presence_of_element_located(locator))
    soup = BeautifulSoup(driver.page_source,'lxml')
    if len(soup.find_all('div',class_='nomsg area')) == 1:
        continue
    houseList = soup.find_all('li',class_='clearfix')
    driver = webdriver.Chrome()
 
    for house in houseList:
        if len(house['class']) > 1:
            continue
        title = house.find('a',class_='t1').string
        littleArea = title.split('·')[1].split('-')[0][:-3]
        amountRoom = int(title.split('·')[1].split('-')[0][-3])
        towards = title.split('·')[1].split('-')[1]
        houseUrl = house.find('a',class_='t1')['href']
        detail = list(house.find('div',class_='detail').stripped_strings)
        frame_1.loc[index,'区'] = "a"
        frame_1.loc[index,'街道'] = "b"
        frame_1.loc[index,'小区'] = littleArea
        frame_1.loc[index,'房间数'] = amountRoom
        frame_1.loc[index,'房间朝向'] = towards
        frame_1.loc[index,'房间网址'] = houseUrl
        frame_1.loc[index,'面积'] = detail[0]
        frame_1.loc[index,'楼层'] = detail[2]
        frame_1.loc[index,'最近地铁距离'] = detail[-1]
        get_price(house)
        input()
        # frame_1.loc[index,'价格'] = getprice(house,numList)
        frame_1.loc[index,'价格'] = 0
        index += 1
    try:
        pageNum = int(soup.find('div',class_='pages').find_all('span')[-4].string[1:-1])
    except IndexError:
        index_1 += 1
        continue
            
    for i in range(2,pageNum+1):
        newUrl = url+'?p=%d'%i
        driver.get(newUrl)    
        locator = (By.ID,'houseList')
        WebDriverWait(driver,10,0.5).until(EC.presence_of_element_located(locator))
        soup = BeautifulSoup(driver.page_source,'lxml')
        houseList = soup.find_all('li',class_='clearfix')
        
        for house in houseList:
            if len(house['class']) > 1:
                continue
            title = house.find('a',class_='t1').string
            littleArea = title.split('·')[1].split('-')[0][:-3]
            amountRoom = int(title.split('·')[1].split('-')[0][-3])
            towards = title.split('·')[1].split('-')[1]
            houseUrl = house.find('a',class_='t1')['href']
            detail = list(house.find('div',class_='detail').stripped_strings)    
            frame_1.loc[index,'区'] = "a"
            frame_1.loc[index,'街道'] = "b"
            frame_1.loc[index,'小区'] = littleArea
            frame_1.loc[index,'房间数'] = amountRoom
            frame_1.loc[index,'房间朝向'] = towards
            frame_1.loc[index,'房间网址'] = houseUrl
            frame_1.loc[index,'面积'] = detail[0]
            frame_1.loc[index,'楼层'] = detail[2]
            frame_1.loc[index,'最近地铁距离'] = detail[-1]
            # frame_1.loc[index,'价格'] = getprice(house,numList)
            frame_1.loc[index,'价格'] = 0
            index += 1
    index_1 += 1
           
frame_1.to_excel('自如爬虫.xlsx')
