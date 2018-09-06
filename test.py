# encoding: utf-8
import os
import time
from aip import AipOcr
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def baiduOCR(picfile):
    filename = os.path.basename(picfile)

    APP_ID = '11781731' # 刚才获取的 ID，下同
    API_KEY = '9s8vYsUven2iOH0aCRTMqzwq'
    SECRECT_KEY = 'KEHongCyBxLwYltgM54bvv4VQyXTN11k'
    client = AipOcr(APP_ID, API_KEY, SECRECT_KEY)

    i = open(picfile, 'rb')
    img = i.read()
    message = client.basicGeneral(img)   # 通用文字识别，每天 50 000 次免费
    #message = client.basicAccurate(img)   # 通用文字高精度识别，每天 800 次免费
    i.close();

    return message["words_result"][0]["words"]

def get_price(imgelement):
	locations = imgelement.location
	sizes = imgelement.size
	rangle = (int(locations['x']),int(locations['y']),int(locations['x'] + sizes['width']),int(locations['y'] + sizes['height']))
	img = Image.open("tmp/screen.png")
	jpg = img.crop(rangle)
	jpg.save("tmp/element.png")
	text = baiduOCR("tmp/element.png")
	return text[1:-3]

dcap = dict(DesiredCapabilities.PHANTOMJS) #设置userAgent
dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 ")
#打开浏览器
wb = webdriver.PhantomJS(desired_capabilities=dcap)
url = 'http://www.ziroom.com/z/nl/z2.html?qwd=%E6%99%BA%E5%AD%A6%E8%8B%91'
wb.maximize_window()

wb.get(url)
wb.save_screenshot("tmp/screen.png")
elements = wb.find_elements_by_xpath('//li[@class="clearfix"]')
for element in elements:
	print(element.get_attribute('innerHTML'))
	price_element = element.find_element_by_xpath('//p[@class="price"]')
	price = get_price(price_element)
	print(price)
