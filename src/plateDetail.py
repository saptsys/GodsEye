import pytesseract
import argparse
import sys
import re
import os
import requests
import cv2
import json 
import numpy as np
from time import sleep
from PIL import Image, ImageEnhance
from bs4 import BeautifulSoup, SoupStrainer
from urllib.request import urlretrieve
from io import BytesIO
import datetime


def resolve(img):
	enhancedImage = enhance()
	return pytesseract.image_to_string(enhancedImage)

def enhance():
	img = cv2.imread('data/downloaded_captcha.png', 0)
	kernel = np.ones((2,2), np.uint8)
	img_erosion = cv2.erode(img, kernel, iterations=1)
	img_dilation = cv2.dilate(img, kernel, iterations=1)
	erosion_again = cv2.erode(img_dilation, kernel, iterations=1)
	final = cv2.GaussianBlur(erosion_again, (1, 1), 0)
	return final


def findOwner(data = None):

	s = requests.Session()

	pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

	app_url = 'https://vahan.nic.in/nrservices/faces/user/searchstatus.xhtml'
	captcha_image_url = 'https://vahan.nic.in/nrservices/cap_img.jsp'
	number = ""
	plate = np.zeros((10,10))
	if(data == None):
		number = sys.argv[1]
	elif(len(data) == 2):
		number = data[0]
		plate = data[1]

	print("PID:"+str(os.getpid())+" "+number+" : finding owner's details...")
	#MARK: Get Request to get webpage elements like textFields, image, etc
	r = s.get(url=app_url)
	cookies = r.cookies
	soup = BeautifulSoup(r.text, 'html.parser')


	#MARK: ViewState contains token which needs to be passed in POST Request
	# ViewState is a hidden element. Open debugger to inspect element 
	viewstate = soup.select('input[name="javax.faces.ViewState"]')[0]['value']


	#MARK: Get Request to get Captcha Image from URL
	## Captcha Image Changes each time the URL is fired
	iresponse = s.get(captcha_image_url)
	img = Image.open(BytesIO(iresponse.content))
	img.save("data/downloaded_captcha.png")


	# print('Resolving Captcha')
	captcha_text = resolve(img)
	extracted_text = str.upper(captcha_text.replace(" ", "").replace("\n", ""))
	# print("OCR Result => ", extracted_text)
	# print(extracted_text)

	# MARK: Identifying Submit Button which will be responsible to make POST Request
	button = soup.find("button",{"type": "submit"})


	encodedViewState = viewstate.replace("/", "%2F").replace("+", "%2B").replace("=", "%3D")

	# MARK: Data, which needs to be passed in POST Request | Verify this manually in debugger
	data = {
		'javax.faces.partial.ajax':'true',
		'javax.faces.source': button['id'],
		'javax.faces.partial.execute':'@all',
		'javax.faces.partial.render': 'rcDetailsPanel resultPanel userMessages capatcha txt_ALPHA_NUMERIC',
		button['id']:button['id'],
		'masterLayout':'masterLayout',
		'regn_no1_exact': number,
		'txt_ALPHA_NUMERIC': extracted_text,
		'javax.faces.ViewState': viewstate,
		'j_idt32':''
	}
	# MARK: Data in Query format.. But not in use for now
	query = "javax.faces.partial.ajax=true&javax.faces.source=%s&javax.faces.partial.execute=%s&javax.faces.partial.render=rcDetailsPanel+resultPanel+userMessages+capatcha+txt_ALPHA_NUMERIC&j_idt42=j_idt42&masterLayout=masterLayout&j_idt32=&regn_no1_exact=%s&txt_ALPHA_NUMERIC=%s&javax.faces.ViewState=%s"%(button['id'], '%40all', number, extracted_text, encodedViewState)


	# MARK: Request Headers which may or may not needed to be passed in POST Request
	# Verify in debugger
	headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0",
	        "Accept": "application/xml, text/xml, */*; q=0.01",
	        "Accept-Language": "en-US,en;q=0.5",
	        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
	        "Faces-Request": "partial/ajax",
	        "X-Requested-With": "XMLHttpRequest"
	}
	# print(headers)

	# print("\nCookie JSESSIONID => ", cookies['JSESSIONID'])
	# print("\nData => \n")
	# print(data)

	# MARK: Added delay
	sleep(2.0)



	#MARK: Send POST Request 
	postResponse = s.post(url=app_url, data=data, headers=headers, cookies=cookies)
	# print("\nPOST Request -> Response =>\n")

	rsoup = BeautifulSoup(postResponse.text, 'html.parser')
	# print("Mark: postResponse soup => ")
	# print(rsoup.prettify())

	#MARK: Following code finds tr which means <table> element from html response
	# the required response is appended in <table> only. Verify it in debugger
	table = SoupStrainer('tr')
	tsoup = BeautifulSoup(rsoup.get_text(), 'html.parser', parse_only=table)

	# print("Table Soup => ")
	# print(tsoup.prettify())
	
	time = datetime.datetime.now()
	# name = "{0}_{1}".format(number,time.strftime("%d%m%Y%H%M%S"))
	name = "{0}".format(number)
	with open("storage\\"+name+".html",'w') as file:
		file.write(("<table border=1><tr><td colspan=2><img src='images/{0}.png' width=200/></td><td colspan=2>{1}</td></tr>".format(name,time)+tsoup.prettify()+"</table>"))
		cv2.imwrite("storage\\images\\"+name+"."+"png",plate)
		print("PID:"+str(os.getpid())+"   "+number+" : owner details saved in storage")
	#MARK: Result Table not appending to the response data
	#Fix Needed



