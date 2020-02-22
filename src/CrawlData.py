import pytesseract
import requests
import cv2
import numpy as np
from bs4 import BeautifulSoup, SoupStrainer
import datetime
import os

class CrawlData():
	def __init__(self,tesseractPath="J:/Program Files/Tesseract-OCR/tesseract.exe"):
			self.tesseractPath = tesseractPath
			# create req session
			self.session = requests.Session()
			
			# define urls
			self.app_url = 'https://vahan.nic.in/nrservices/faces/user/searchstatus.xhtml'
			self.captcha_image_url = 'https://vahan.nic.in/nrservices/cap_img.jsp'

			# load site
			site = self.session.get(url=self.app_url)
			self.cookies = site.cookies
			soup = BeautifulSoup(site.text, 'html.parser')
			self.viewstate = soup.select('input[name="javax.faces.ViewState"]')[0]['value']

			# get captcha
			self.captcha = self.generateCaptcha()
			# convert to np array from byte string
		
			self.button = soup.find("button",{"type": "submit"})

			self.headers = {
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0",
				"Accept": "application/xml, text/xml, */*; q=0.01",
				"Accept-Language": "en-US,en;q=0.5",
				"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
				"Faces-Request": "partial/ajax",
				"X-Requested-With": "XMLHttpRequest"
			}
			print("Crawler initialized")
	
	def generateCaptcha(self):
		iresponse = self.session.get(self.captcha_image_url)
		img = cv2.imdecode(np.fromstring(iresponse.content, np.uint8), cv2.IMREAD_COLOR)
		self.captcha = str.upper(self.resolve(img).replace(" ", "").replace("\n", ""))
		return self.captcha

	def resolve(self,img):
			pytesseract.pytesseract.tesseract_cmd = self.tesseractPath
			enhancedImage = self.enhance(img)
			return pytesseract.image_to_string(enhancedImage)

	def enhance(self,img):
		kernel = np.ones((2,2), np.uint8)
		img_erosion = cv2.erode(img, kernel, iterations=1)
		img_dilation = cv2.dilate(img, kernel, iterations=1)
		erosion_again = cv2.erode(img_dilation, kernel, iterations=1)
		final = cv2.GaussianBlur(erosion_again, (1, 1), 0)
		return final

	def fetch(self,plates,recaptcha=True):
		number = ""
		plate = np.zeros((10,10))
		if(len(plates) == 2):
			number = plates[0]
			plate = plates[1]
		data = {
			'javax.faces.partial.ajax':'true',
			'javax.faces.source': self.button['id'],
			'javax.faces.partial.execute':'@all',
			'javax.faces.partial.render': 'rcDetailsPanel resultPanel userMessages capatcha txt_ALPHA_NUMERIC',
			self.button['id']:self.button['id'],
			'masterLayout':'masterLayout',
			'regn_no1_exact': number,
			'txt_ALPHA_NUMERIC': self.captcha,
			'javax.faces.ViewState': self.viewstate,
			'j_idt32':''
		}

		postResponse = self.session.post(url=self.app_url, data=data, headers=self.headers, cookies=self.cookies)
		rsoup = BeautifulSoup(postResponse.text, 'html.parser')
		table = SoupStrainer('tr')
		tsoup = BeautifulSoup(rsoup.get_text(), 'html.parser', parse_only=table).prettify()

		if(tsoup == "" and recaptcha == True):
			self.generateCaptcha()
			self.fetch(plates,False)
		else:
    			if(tsoup == ""):
    					tsoup = rsoup.get_text()

		time = datetime.datetime.now()
		name = "{0}_{1}".format(number,time.strftime("%d-%m-%Y %H.%M.%S"))
		with open("storage\\"+name+".html",'w') as file:
			file.write(("<table border=1><tr><td colspan=2><img src='images/{0}.png' width=200/></td><td colspan=2>{1}</td></tr>".format(name,time)+tsoup+"</table>"))
			cv2.imwrite("storage\\images\\"+name+"."+"png",plate)
			print("PID:"+str(os.getpid())+"   "+number+" : owner details saved in storage")

		return tsoup

# crawlData = CrawlData()
# crawlData.fetch(["GJ03AB0639",[]])