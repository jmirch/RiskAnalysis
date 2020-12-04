from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time
from prettytable import PrettyTable
from prettytable import ALL

driver = webdriver.Chrome("/usr/local/bin/chromedriver")

driver.get("https://dominating12.com/game/1096090")
time.sleep(1)
gameLogTab = driver.find_element_by_id('game-log-tab-link')
driver.execute_script("arguments[0].click();", gameLogTab)
time.sleep(1)
loadButton = driver.find_element_by_id('load-log')
driver.execute_script("arguments[0].click();", loadButton)
time.sleep(2)
content = driver.page_source
soup = BeautifulSoup(content, "html.parser")

# Initialize maps
defend = {}
attack = {}

for div in soup.findAll('div', attrs={'class':'chat-message-body'}):
    if "attacked" in div.text:
        # Use regex to get names and troop counts killed/lost
        names = re.findall('\(([a-zA-Z0-9]*)\)', div.text)
        killed = int(re.findall('killing\s(\d{1,2})', div.text)[0])
        lost = int(re.findall('losing\s(\d{1,2})', div.text)[0])
        first = str(names[0])
        second = str(names[1])
        
        # Initialize players in map if they havent been
        # Tuples are defined as (killed, lost)
        if first not in attack:
            attack[first] = [0, 0]
        if second not in defend:
            defend[second] = [0, 0]

        # Increment counts
        currCount = attack[first]
        currCount[0] = currCount[0] + killed
        currCount[1] = currCount[1] + lost

        defendCurrCount = defend[second]
        defendCurrCount[0] = defendCurrCount[0] + lost
        defendCurrCount[1] = defendCurrCount[1] + killed
        
driver.close()

# Format data as table and print
t = PrettyTable(["Name", "Killed", "Lost", "KD", "Killed Attack",
    "Lost Attack", "Attack KD", "Killed Defending", "Lost Defending", "Defend KD"])
t.hrules = ALL
for name in attack:
    currAttack = attack[name]
    currDefend = defend[name]
    totalKilled = currAttack[0] + currDefend[0]
    totalLost = currAttack[1] + currDefend[1]
    t.add_row([name, totalKilled, totalLost, "{:.1F}".format(float(totalKilled)/float(totalLost)),
        currAttack[0], currAttack[1], "{:.1F}".format(float(currAttack[0])/float(currAttack[1])),
        currDefend[0], currDefend[1], "{:.1F}".format(float(currDefend[0])/float(currDefend[1])) ])

print(t)