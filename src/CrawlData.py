import pytesseract
import requests
import cv2
import numpy as np
from bs4 import BeautifulSoup, SoupStrainer
import datetime
import os
import re
import json
from database import Database

class CrawlData():
	def __init__(self,settings):
			self.settings = settings
			self.isDisabled = False
			self.tesseractPath = settings['tesseract']
			self.database = Database(settings['dataBase'])
			# create req session
			self.session = requests.Session()
			
			# define urls
			self.app_url = 'https://vahan.nic.in/nrservices/faces/user/searchstatus.xhtml'
			self.captcha_image_url = 'https://vahan.nic.in/nrservices/cap_img.jsp'

			try:
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
			except ConnectionError as ex:
				self.isDisabled = True
				print("check your internet connection, "+str(ex))
			except Exception as ex:
				self.isDisabled = True
				print("Error in Crawler : "+str(ex))
	
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
	
	def cleanHTML(self,raw_html):
			try:	
				cleanr = re.compile('<.*?>')
				cleantext = re.sub(cleanr, '', raw_html)
				return cleantext
			except:
				return ""

	def writeData(self,jsonObj,img):
			with open("storage/results.json", "r+") as file:
				data = json.load(file)
				data.append(jsonObj)
				file.seek(0)
				json.dump(data, file,indent=3)

	def extractJson(self,content,soup):
		jsonObj = {}
		try:
			jsonObj['Registering Authority'] =  self.cleanHTML( soup.find("div",{"class":"text-capitalize"}).text).split(":")[1].strip()
			for i in range(0,len(content),2):
				key = self.cleanHTML(content[i].text).replace(":","").strip()
				value = self.cleanHTML(content[i+1].text).strip()
				jsonObj[key] = value
				# jsonObj['isFound'] = True
		except:
			jsonObj['isFound'] = False
		
		timeStamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		jsonObj['Timestamp'] = timeStamp
		return jsonObj

	def fetch(self,plates,recaptcha=True):
			if self.isDisabled:
				exit(1)
			try:
				number = ""
				plate_img = np.zeros((10,10))
				if(len(plates) == 2):
					number = plates[0]
					plate_img = plates[1]
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
				rsoup = BeautifulSoup(postResponse.text, 'html.parser').text

				rsoup = rsoup.replace("<![CDATA[","")
				rsoup = rsoup.replace("]]>",">")
				rsoup = BeautifulSoup(rsoup,'html.parser')
				# print(rsoup)
				errmsg = self.cleanHTML(rsoup.find("div",{"id":"userMessages"}).text)
				if(errmsg != ""):
						print("HTML Cleaning Error : "+errmsg)
						if(recaptcha == True):
								self.generateCaptcha()
								return self.fetch(plates,False)
						else:
								print(self.captcha)
								return

				resultPanel = rsoup.find("div", {"id": "rcDetailsPanel"}).find_all('div', attrs={'class':'fit-width-content'})

				jsonObj = self.extractJson(resultPanel,rsoup)
				# self.writeData(jsonObj,plate_img)
				self.database.insertPlates(number,jsonObj["Owner Name"],plate_img,json.dumps(jsonObj))
				return json.dumps(jsonObj,indent=3)
			except Exception as ex:
				print("Exception At PID {0} : {1}".format(os.getpid(),ex))
				exit(0)

# crawlData = CrawlData(set.Settings())
# print(crawlData.fetch(["GJ14S9565",[]]))
