# encoding: utf-8
import os
import time
import datetime
import pandas as pd
from urllib import parse
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
	return text[1:]

def modify_price(price):
	if price[-1] != ')':
		price += ')'
	if "每天" in price:
		month_price = int(price[:-4])*30
	else:
		month_price = int(price[:-4])
	return price, month_price

dcap = dict(DesiredCapabilities.PHANTOMJS) 
dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36")
wb = webdriver.PhantomJS(desired_capabilities=dcap)
# url = 'http://www.ziroom.com/z/nl/z2.html?qwd=%E6%99%BA%E5%AD%A6%E8%8B%91'
wb.maximize_window()

community_list = ["智学苑", "领秀新硅谷", "铭科苑", "燕尚园", "上地西里", "上地东里小区", "上地佳园", "怡美家园", "当代城市家园", "今佳园", "金隅•美和园西区", "马连洼北路1号院"]
# , "上地MOMA"
result = []
for i, community in enumerate(community_list):
	print("{0} {1}/{2}".format(community, i+1, len(community_list)))
	url = "http://www.ziroom.com/z/nl/z2.html?qwd={0}".format(parse.quote(community))
	wb.get(url)
	time.sleep(2)
	try:
		total_page_num = wb.find_element_by_xpath('//div[@class="pages"]').find_element_by_tag_name("span").text[1:-1]
	except:
		total_page_num = 1
	total_page_num = int(total_page_num)
	for _ in range(total_page_num):
		time.sleep(2)
		wb.save_screenshot("tmp/screen.png")
		elements = wb.find_elements_by_xpath('//li[@class="clearfix"]')
		try:
			next_button = wb.find_element_by_xpath('//a[@class="next"]')
		except:
			next_button = None

		for element in elements:
			house_detail = element.find_element_by_class_name("txt")
			house_name = house_detail.find_element_by_tag_name("h3").text
			house_url = house_detail.find_element_by_tag_name("h3").find_element_by_tag_name("a").get_attribute("href")
			# print(house_url)
			house_location = house_detail.find_element_by_tag_name("h4").text
			house_info = house_detail.find_elements_by_tag_name("p")
			house_size = house_info[0].text
			house_accu_location = house_info[1].text
			price = get_price(element.find_element_by_class_name('price'))
			price, month_price = modify_price(price)
			item = (community, house_name, house_url, house_location, house_size, house_accu_location, price, month_price)
			result.append(item)

		if next_button is None:
			break
		else:
			# print("click next button")
			next_button.click()

result = pd.DataFrame(result, columns=['小区名字', '房间名字', '房间url', '房间位置', '房间大小', '房间具体位置', '价格', '每月价格'])
writer = pd.ExcelWriter("data/{0}.xlsx".format(datetime.date.today()))
result.to_excel(writer, index=False)
writer.save()
