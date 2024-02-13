from bs4 import BeautifulSoup as bs
from pprint import pprint
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os
import datetime
import json
import sys

username = ""
password = ""
old_code = ["MFL", "UITASBNK"]
new_code = ["EPIGRAL", "EQUITASBNK"]
week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
sector = {}
marcap = {}

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
# chrome stores profiles
options.add_argument(r"--user-data-dir=/home/ayman/.config/google-chrome")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)
driver.get("https://www.screener.in/login/?")
try:
	driver.find_element(By.XPATH, "//*[@id='id_username']").send_keys(username)
	driver.find_element(By.XPATH, "//*[@id='id_password']").send_keys(password)
	driver.find_element(By.XPATH, "/html/body/main/div[2]/div[2]/form/button").click()
except:
	pass

def main():
	#os.system('clear')
	marcap={}
	sector={}
	if len(sys.argv) < 2:
		print("\n What data do you want:\n\n  1. Run\n  2. Analyze\n  3. Top Gainers\n  4. Top Losers\n  5. Clear Data\n  6. Exit\n")
		choice = input(" Choose selection: ")
	else:
		choice = sys.argv[1]
	if choice=="1" :
		start(1)
		start(0)
		print_sector_cap(True)
	elif choice=="2" :
		analyze()
	elif choice=="3" :
		start(0)
		print_sector_cap(False)
	elif choice=="4" :
		start(1)
		print_sector_cap(False)
	elif choice=="5" :
		clear_db()
	else:
		exit()

	del(choice)


def search(name):
	#print(".")

	if name in old_code:
		name = new_code[old_code.index(name)]
	driver.get("https://www.screener.in/company/"+name+"/consolidated/")
	time.sleep(2)
	bl = 1
	try:
		# check for YoY Quat Sales
		if(driver.find_element(By.XPATH, "//*[@id='top-ratios']/li[19]/span[2]").text=="%" or driver.find_element(By.XPATH,"//*[@id='top-ratios']/li[16]/span[2]/span").text==""):
			raise Exception
	except:
		#time.sleep(2)
		driver.get("https://www.screener.in/company/"+name+"/")
		time.sleep(2)
		#print("going to standalone " + name)
	if( float(driver.find_element(By.XPATH, "//*[@id='top-ratios']/li[16]/span[2]/span").text) >= 1 ):
		bl=0
	elif( float(driver.find_element(By.XPATH, "//*[@id='top-ratios']/li[17]/span[2]/span").text) >= 1 ):
		bl=0
	elif( float(driver.find_element(By.XPATH, "//*[@id='top-ratios']/li[18]/span[2]/span").text) >= 1 ):
		bl=0

	if(bl==0):
		return False

	try:
		driver.find_element(By.XPATH, "//*[@id='quarters']/div[3]/table/tbody/tr[1]/td[1]/button").send_keys('\n')#click()
		time.sleep(3)		# make it 2 if slow
		sales = driver.find_element(By.XPATH, "//*[@id='quarters']/div[3]/table/tbody/tr[2]")
	except:
		try:
			driver.find_element(By.XPATH, "//*[@id='quarters']/div[2]/table/tbody/tr[1]/td[1]/button").send_keys('\n')#click()
			time.sleep(3)		# make it 2 if slow
			sales = driver.find_element(By.XPATH, "//*[@id='quarters']/div[2]/table/tbody/tr[2]")
		except:
			# Its a bank
			return False
	if sales.find_element(By.TAG_NAME,"td").text!="YOY Sales Growth %":		# Latest Patch
		time.sleep(1)
		print("Had to rerun sales")
		try:
			driver.find_element(By.XPATH, "//*[@id='quarters']/div[3]/table/tbody/tr[1]/td[1]/button").send_keys('\n')#click()
			time.sleep(3)		# make it 2 if slow
			sales = driver.find_element(By.XPATH, "//*[@id='quarters']/div[3]/table/tbody/tr[2]")
		except:
			try:
				driver.find_element(By.XPATH, "//*[@id='quarters']/div[2]/table/tbody/tr[1]/td[1]/button").send_keys('\n')#click()
				time.sleep(3)		# make it 2 if slow
				sales = driver.find_element(By.XPATH, "//*[@id='quarters']/div[2]/table/tbody/tr[2]")
			except:
				return False	# Its a bank
	sales_list = []
	for x in range(1,len(sales.find_elements(By.TAG_NAME,"td"))):
		if(sales.find_elements(By.TAG_NAME, "td")[x].text != ""):
			sales_list.append(sales.find_elements(By.TAG_NAME, "td")[x].text)
	del(sales)
	for x in sales_list[-4:]:
		if(x=="" or x=="0.00" or x=="-0.00"):
			return False
		if(x[-1]!='%'):
			raise Exception("Not percentage "+ name +" "+ x)
		x=x.replace(",","")
		x=x.replace("%","")
		if(float(x)<1):
			bl=0
	#print(*sales_list, sep='  ')
	del(sales_list)
	return bool(bl)


def start(flag):
	global marcap, sector
	print("\n\n+---------------------------------+")
	print("|                                 |")
	if(flag==0):
		file1 = open("top_gainers.txt", "w")
		file1.write("\n\tTop Gainers \n\n")
		url = "https://mintgenie.livemint.com/markets/details/top_gainers"
		print("|           Top Gainers           |")
	else:
		file1 = open("top_losers.txt", "w")
		file1.write("\n\tTop Losers \n\n")
		url = "https://mintgenie.livemint.com/markets/details/top_losers"
		print("|            Top Loser            |")
	print("|                                 |")
	print("+---------------------------------+\n\n")

	# setup the list
	driver.get(url)
	time.sleep(3)
	driver.find_element(By.XPATH, "//*[@id='__next']/main/div[3]/div[3]/div/div/div/div["+str(2+flag)+"]/div/div/div[1]/div/ul/li[2]/div/label").click()
	driver.find_element(By.XPATH, "//*[@id='__next']/main/div[3]/div[3]/div/div/div/div["+str(2+flag)+"]/div/div/div[2]/div[1]/div/div/span[2]").click()
	time.sleep(2)
	driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/div[2]/div[1]/div/div/div[3]/div").click()
	time.sleep(2)

	# Load more
	tick = True
	while tick:
		tick = False
		for x in driver.find_elements(By.CLASS_NAME, "load-more-btn") :
			if(x.text == "Load More"):
				x.find_element(By.TAG_NAME, "button").send_keys("\n")
				tick= True
				time.sleep(2)

	# setup database
	count=0
	table=[]
	time.sleep(2)
	for x in driver.find_element(By.XPATH,"//*[@id='__next']/main/div[3]/div[3]/div/div/div/div["+str(2+flag)+"]/div/div/div[3]/div[1]/ul").find_elements(By.TAG_NAME, "li"):
		count = count+1
		if(count==1):
			continue
		ele =[]		# ele[ url, name, change, code, cap, sector]
		ele.append(x.find_element(By.TAG_NAME, "a").get_attribute("href"))
		ele.append(x.find_element(By.CLASS_NAME, "company-name").text)
		ele.append(x.find_element(By.CLASS_NAME, "list-percentage").text.replace("%",""))
		try:
			if((float(ele[2]) > -1.0 and flag==1) or (float(ele[2]) < 1.0 and flag==0)):
				del ele
				break
		except:
			print("empty change of "+ ele[1])
		table.append(ele)
		del ele

	# add nse code to database
	xtra= []
	for y in table:
		driver.get(y[0])
		time.sleep(1)
		try:
			code = driver.find_element(By.CLASS_NAME, "stock_descriptioninfo__YJ1DH").find_elements(By.TAG_NAME, "li")[1].find_element(By.TAG_NAME, "span").text
			if(code == ""):
				time.sleep(5)
				code = driver.find_element(By.CLASS_NAME, "stock_descriptioninfo__YJ1DH").find_elements(By.TAG_NAME, "li")[1].find_element(By.TAG_NAME, "span").text
			y.append(code)
			cap = driver.find_element(By.CLASS_NAME, "stock_descriptionlist__1TlJM").find_elements(By.TAG_NAME, "li")[0].text
			if(cap==""):	# Latest patch
				time.sleep(2)
				cap = driver.find_element(By.CLASS_NAME, "stock_descriptionlist__1TlJM").find_elements(By.TAG_NAME, "li")[0].text
				print("Had to rerun cap")
				if(cap==""):
					time.sleep(5)
					cap = driver.find_element(By.CLASS_NAME, "stock_descriptionlist__1TlJM").find_elements(By.TAG_NAME, "li")[0].text
			y.append(cap)
			sec = driver.find_element(By.CLASS_NAME, "stock_descriptionlist__1TlJM").find_elements(By.TAG_NAME, "li")[1].text
			if(sec==""):	# Latest patch
				time.sleep(2)
				sec = driver.find_element(By.CLASS_NAME, "stock_descriptionlist__1TlJM").find_elements(By.TAG_NAME, "li")[1].text
				print("Had to rerun sec")
				if(sec==""):	# Latest patch
					time.sleep(3)
					sec = driver.find_element(By.CLASS_NAME, "stock_descriptionlist__1TlJM").find_elements(By.TAG_NAME, "li")[1].text
			if sec=="":
				print("No sec for "+ y[0])
				sec = "Miscellaneous"
			if cap == "":
				print("No cap for "+ y[0])
			y.append(sec)
			if cap in marcap:
				marcap[cap] = round(marcap[cap] + float(y[2]), 2)
			else:
				marcap[cap] = float("{:.2f}".format(float(y[2])))		# round(float(y[2]),2)
			if sec in sector:
				sector[sec] = round(sector[sec] + float(y[2]), 2)
			else:
				sector[sec] = float("{:.2f}".format(float(y[2])))
			del cap, sec
		except:
			print("Cant find NSE code of " + y[0])
			driver.get_screenshot_as_file("mint.png")
			xtra.append(y[1])
			continue
		try:
			if search(y[3]):
				print(y[3].ljust(10) +"\t"+ y[2].ljust(4) +"\t"+ y[4].ljust(10) + y[5])
				file1.write(y[3].ljust(10) +"\t"+ y[2].ljust(10) +"\t"+ y[1].ljust(4) + "\n")
		except Exception as e :
			print(str(e) +"\n"+ driver.current_url)
			driver.get_screenshot_as_file("screener.png")
	del count

	# screen the database
	#try:
		#for y in table:
			#if(len(y)==6 and search(y[3])):
				#print(y[3].ljust(10) +"\t"+ y[2].ljust(4) +"\t"+ y[4].ljust(10) + y[5])
				#file1.write(y[3].ljust(10) +"\t"+ y[2].ljust(10) +"\t"+ y[1].ljust(4) + "\n")
			#time.sleep(3)
	#except Exception as error :
		#print(error)
		#print(driver.current_url)
		#driver.get_screenshot_as_file("screenshot.png")
	print(xtra)
	file1.write(datetime.datetime.now().strftime("\n\n" + "%Y-%m-%d %H:%M:%S"))
	file1.close()


def print_sector_cap(flag1):
	global marcap, sector
	sorted_cap = sorted(marcap.items(), key = lambda x:x[1], reverse=True)
	marcap = dict(sorted_cap)
	sorted_sec = sorted(sector.items(), key = lambda x:x[1], reverse=True)
	sector = dict(sorted_sec)
	del sorted_cap, sorted_sec
	print("\n")
	for keys, values in marcap.items():
		print(keys.ljust(10) + str(values))
	print("\n")
	for keys, values in sector.items():
		print(keys.ljust(40) + str(values))
	if not flag1:
		return
	# read data
	day = datetime.datetime.today().weekday()
	json_data = []
	with open('data.json') as json_file:
		json_data = json.load(json_file)
	# format data
	temp = []
	temp.append(marcap)
	temp.append(sector)
	temp.append(datetime.date.today().strftime("%d/%m/%Y"))
	json_data[day] = temp
	# write data
	with open('data.json', 'w') as fout:
		json.dump(json_data, fout)
	del json_data, temp, day


def analyze():
	data = []
	sec = {}
	cap = {}
	with open('data.json') as json_file:
		data = json.load(json_file)
	print("\n Which day(s) you want analysis of\n 1. All\n 2. Monday\n 3. Tuesday\n 4. Wednesday\n 5. Thursday\n 6. Friday\n")
	iin = int(input(" Choose selection : "))
	print("\n Analyzing data of :")
	if iin < 7 and iin>1:
		if len(data[iin-2])==0:
			print("\n No data exists for selected date")
			return
		print("  " + data[iin-2][2])
		cap = data[iin-2][0]
		sec = data[iin-2][1]
	elif iin==1:
		for z in data:
			if len(z)==0 :
				continue
			for key, value in z[0].items():
				if key in cap:
					cap[key] = round(cap[key] + value, 2)
				else:
					cap[key] = round(value,2)
			for key, value in z[1].items():
				if key in sec:
					sec[key] = round(sec[key] + value, 2)
				else:
					sec[key] = round(value,2)
			print("  "+ z[2])
	else:
		return
	# sort analysis
	sorted_cap = sorted(cap.items(), key = lambda x:x[1], reverse=True)
	sorted_sec = sorted(sec.items(), key = lambda x:x[1], reverse=True)
	# print analysis
	print("\n")
	for keys, values in sorted_cap:
		print(keys.ljust(10) + str(values))
	print("\n")
	for keys, values in sorted_sec:
		print(keys.ljust(40) + str(values))
	del sorted_cap, sorted_sec, data, cap, sec


def clear_db():
	with open('data.json') as json_file:
		data = json.load(json_file)
	ind = int(input("\n Enter day to clear (Mon-Fri => 1-5) : ")) - 1
	data[ind] = []
	with open('data.json', 'w') as fout:
		json.dump(data, fout)
	print(" Data cleared for "+ week[ind])
	del data, ind

if __name__ == "__main__":
    main()
