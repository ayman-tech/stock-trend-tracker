from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import datetime
import json
import sys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#from selenium.webdriver.common.keys import Keys

from properties import username, password, old_code, new_code, reject, watchlist
week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
debug = False
sector = {}
marcap = {}

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
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
	news_list = []
	global debug
	#print("\n Watchlist \n")
	#if len(watchlist) :
		#for watch in watchlist :
			#driver.get("https://finance.yahoo.com/quote/" + watch + ".NS")
			#time.sleep(2)
			## get % change from google finance
			#try:
				#watch_change = driver.find_element(By.XPATH,
					#"//*[@id=\"nimbus-app\"]/section/section/section/article/section[1]/div[2]/div[1]/section/div/section/div[1]/fin-streamer[3]").text
			#except:
				#print("\n  E :  ERROR yahoo fin element not found")
				#break;
			#print(watch.ljust(10) + "    " + watch_change[1:-1])
	print("\ncheck")
	if len(sys.argv) < 2:
		print("\n What data do you want:\n\n  1. Run\n  2. Analyze\n  3. Top Gainers\n  4. Top Losers\n  5. Clear Data\n  6. Exit\n")
		choice = input(" Choose selection: ")
	else:
		choice = sys.argv[1]
	print("choice : "+choice)
	if choice[0] == 'd':
		debug = True
		print("\n  D : Debug Mode ON")
		choice = choice[1:]
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
	input("\n Press enter to exit")


def search(name):
	if debug : print("\n  D : Screening " + name)
	if name in reject:
		return False
	if name in old_code:
		name = new_code[old_code.index(name)]
		if debug : print("	D : Change code to " + name)
	driver.get("https://www.screener.in/company/"+name+"/consolidated/")
	time.sleep(2)
	bl = 1
	try:
		if(driver.find_element(By.XPATH, "//*[@id='top-ratios']/li[19]/span[2]").text=="%" or driver.find_element(By.XPATH,"//*[@id='top-ratios']/li[16]/span[2]/span").text==""):
			if debug : print("	D : YoY Qtr Sales ratio not found. Rejected")
			return
	except:
		#time.sleep(2)
		driver.get("https://www.screener.in/company/"+name+"/")
		time.sleep(2)
		try:
			if(driver.find_element(By.XPATH, "//*[@id='top-ratios']/li[19]/span[2]").text=="%" or driver.find_element(By.XPATH,"//*[@id='top-ratios']/li[16]/span[2]/span").text==""):
				if debug : print("	D : YoY Qtr Sales ratio not found. Rejected")
				return
			if debug : print("	D : Going to Standalone")
		except:
			return
	if( float(driver.find_element(By.XPATH, "//*[@id='top-ratios']/li[16]/span[2]/span").text) >= 1 ):
		bl=0
	elif( float(driver.find_element(By.XPATH, "//*[@id='top-ratios']/li[17]/span[2]/span").text) >= 1 ):
		bl=0
	elif( float(driver.find_element(By.XPATH, "//*[@id='top-ratios']/li[18]/span[2]/span").text) >= 1 ):
		bl=0
	elif( driver.find_element(By.XPATH, "//*[@id='top-ratios']/li[4]/span[2]").text == "" ):
		bl=0	# p/e ratio not present
	
	if(bl==0):
		if debug : print("	D : Ratio Conditions Failed. Rejected")
		return False

	try:
		driver.find_element(By.XPATH, "//*[@id='quarters']/div[3]/table/tbody/tr[1]/td[1]/button").send_keys('\n')#click()
		time.sleep(3)		# make it 2 if slow
		sales = driver.find_element(By.XPATH, "//*[@id='quarters']/div[3]/table/tbody/tr[2]")
	except:
		if debug : print("	D : Checking next table")
		try:
			driver.find_element(By.XPATH, "//*[@id='quarters']/div[2]/table/tbody/tr[1]/td[1]/button").send_keys('\n')#click()
			time.sleep(3)		# make it 2 if slow
			sales = driver.find_element(By.XPATH, "//*[@id='quarters']/div[2]/table/tbody/tr[2]")
		except:
			if debug : print("	D : Its a bank")
			return False
	if sales.find_element(By.TAG_NAME,"td").text!="YOY Sales Growth %":
		if debug : print("	D : Had to rerun sales")
		try:
			driver.find_element(By.XPATH, "//*[@id='quarters']/div[3]/table/tbody/tr[1]/td[1]/button").send_keys('\n')#click()
			time.sleep(3)		# make it 2 if slow
			sales = driver.find_element(By.XPATH, "//*[@id='quarters']/div[3]/table/tbody/tr[2]")
		except:
			if debug : print("	D : Checking next table")
			try:
				driver.find_element(By.XPATH, "//*[@id='quarters']/div[2]/table/tbody/tr[1]/td[1]/button").send_keys('\n')#click()
				time.sleep(3)		# make it 2 if slow
				sales = driver.find_element(By.XPATH, "//*[@id='quarters']/div[2]/table/tbody/tr[2]")
			except:
				if debug : print("	D : Its a bank")
				return False
	sales_list = []
	for x in range(1,len(sales.find_elements(By.TAG_NAME,"td"))):
		if(sales.find_elements(By.TAG_NAME, "td")[x].text != ""):
			sales_list.append(sales.find_elements(By.TAG_NAME, "td")[x].text)
	del(sales)
	for x in sales_list[-4:]:
		if(x=="" or x=="0.00" or x=="-0.00"):
			if debug : print("	D : No growth in Sales. Rejected")
			return False
		if(x[-1]!='%'):
			if debug : print("	D : ERROR Not Percentage " + name + " " + x)
			raise Exception("Not percentage "+ name +" "+ x)
		x=x.replace(",","")
		x=x.replace("%","")
		if(float(x)<1):
			if debug : print("	D : Sales growth too low. Rejected")
			bl=0
	#print(*sales_list, sep='  ')
	del(sales_list)
	return bool(bl)


def start(flag):
	global marcap, sector
	print("\n\n+---------------------------------+")
	print("|                                 |")
	url = "https://www.niftyindices.com/market-data/top-gainers-losers"
	if(flag==0):
		file1 = open("top_gainers.txt", "w")
		if debug : print("	D : top gainers file open : " + ("Failure" if file1.closed else "Success"))
		file1.write("\n\tTop Gainers \n\n")
		print("|           Top Gainers           |")
	else:
		file1 = open("top_losers.txt", "w")
		if debug : print("	D : top losers file open : " + ("Failure" if file1.closed else "Success"))
		file1.write("\n\tTop Losers \n\n")
		print("|            Top Loser            |")
	print("|                                 |")
	print("+---------------------------------+\n\n")

	# setup the list
	try:
		driver.get(url)
	except:
		print(" Error : Timeout for "+ url)
		driver.get_screenshot_as_file("nseindia.png")
		return
	if debug : print("	D : Open url " + url)
	time.sleep(3)
	if(flag==1):
		driver.find_element(By.XPATH, "//*[@id='mainInner_C002_Col00']/div[3]/div/div[3]/div/ul/li[2]/a").click()
		time.sleep(5)
	driver.find_element(By.XPATH, "/html/body/form/div[3]/div/div/div/div[2]/div/div/div/div/div/div[3]/div/div[1]/a").click()
	time.sleep(7)
	driver.find_element(By.XPATH, "//*[@id='mCSB_1_container']/li[5]").click()
	time.sleep(10)

	# Load more
	#tick = True
	#while tick:
		#tick = False
		#for x in driver.find_elements(By.CLASS_NAME, "load-more-btn") :
			#if(x.text == "Load More"):
				#x.find_element(By.TAG_NAME, "button").send_keys("\n")
				#if debug : print("	D : Load More clicked")
				#tick= True
				#time.sleep(2)

	# setup database
	count=0
	table=[]
	time.sleep(5)
	if debug : print("	D : Setting up list of stocks")
	if(flag==1):
		xpath = "//*[@id='stockwatchtableLosers']/tbody"
	else:
		xpath = "//*[@id='stockwatchtableGainers']/tbody"
	for x in driver.find_element(By.XPATH,"//*[@id='stockwatchtableLosers']/tbody").find_elements(By.TAG_NAME, "tr"):
		count = count+1
		#elif count>20:
			#break
		ele =[]		# ele[code, change]
		ele.append(x.find_elements(By.TAG_NAME, "td")[0].text)
		ele.append(x.find_elements(By.TAG_NAME, "td")[1].text.replace("%",""))
		try:
			if((float(ele[1]) <= -1.0 and flag==1) or (float(ele[1]) >= 1.0 and flag==0)):
				table.append(ele)
		except:
			if debug : print("	D : No change for " + ele[0])
		del ele

	# add cap & sector
	errored= []
	rejected = []
	if flag==1 : file3 = open("UrlChanger/urls.txt", "w")
	for y in table:
		#driver.get("https://www.nseindia.com/get-quotes/equity?symbol=" + y[0])
		#time.sleep(5)
		#try:
			#sec = driver.find_element(By.XPATH,"//*[@id='peers']/div[1]/div[1]/p/a[1]")
			#y.append(sec)

			#if sec=="":
				#if debug : print("	D : No sector for " + y[0])
				#sec = "Miscellaneous"
			#y.append(sec)

			#if sec in sector:
				#sector[sec] = round(sector[sec] + float(y[2]), 2)
			#else:
				#sector[sec] = float("{:.2f}".format(float(y[2])))
			#del sec
		#except:
			#if debug : print("	D : Cant find sector for " + y[0] + ". Saving ss")
			#driver.get_screenshot_as_file("quote.png")
			#errored.append(y[0])
			#continue

		## reject sectors
		#flag2 = False
		#for word in reject:
			#if word in y[2]:
				#rejected.append(y[0])
				#flag2 = True
				#break
		#if flag2:
			#if debug : print("	D : Rejected Sector "+ y[2])
			#continue

		# search screener for code and write url
		try:
			if search(y[0]):
				print(y[0].ljust(10) +"\t"+ y[1].ljust(4))# +"\t"+ y[4].ljust(10) + y[5])
				file1.write(y[0].ljust(10) +"\t"+ y[1].ljust(10) + "\n")# +"\t"+ y[1].ljust(4) + "\n")
				if flag==1 : file3.write("https://in.tradingview.com/chart/?symbol=NSE%3A"+y[0] + " ")
		except Exception as e :
			print(str(e) +"\n"+ driver.current_url)
			if debug : print("	D : ERROR : " + str(e) +"\n"+ driver.current_url + ". Saving ss")
			driver.get_screenshot_as_file("screener.png")
	
	del count
	if debug : print("	D : Error Processing " + errored)
	if debug : print("	D : Discarded " + rejected)
	file1.write(datetime.datetime.now().strftime("\n\n" + "%Y-%m-%d %H:%M:%S"))
	file1.close()
	if flag==1 : file3.close()


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
	if day>5:
		return;
	json_data = []
	try:
		json_file = open('data.json')
	except:
		file2 = open("data.json", "w")
		file2.write("[[], [], [], [], []]")
		file2.close()
		json_file = open('data.json')
	json_data = json.load(json_file)
	json_file.close()
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
