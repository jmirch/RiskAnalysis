from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import re
import time
from prettytable import PrettyTable
from prettytable import ALL

driver = webdriver.Chrome("/usr/local/bin/chromedriver")

driver.get("https://dominating12.com/game/1097030")
time.sleep(1)
gameLogTab = driver.find_element_by_id('game-log-tab-link')
driver.execute_script("arguments[0].click();", gameLogTab)
time.sleep(1)

# Load more button not always there. Depends on length of game
try:
    loadButton = driver.find_element_by_id('load-log')
    driver.execute_script("arguments[0].click();", loadButton)
    time.sleep(2)
except NoSuchElementException: 
    print "Load more button not present"

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

        # Handle capturing names
        # In some maps, names might be in the format of CountryShortName (CountryLongName) (PlayerName)
        # Elif and Else capture edge cases
        first, second = "", ""
        if len(names) == 2:
            first = str(names[0])
            second = str(names[1])
        elif len(names) == 4:
            first = str(names[1])
            second = str(names[3])
        else:
            second = names[2]
            if names[0] in attack:
                first = names[0]
            elif names[1] in attack:
                first = names[1]
            else: 
                print "Could not identify name of attacker"
                first = "Unknown"

        # Initialize players in map if they havent been
        # Tuples are defined as (killed, lost)
        if first not in attack:
            attack[first] = [0, 0]
        if first not in defend:
            defend[first] = [0, 0]
        if second not in attack:
            attack[second] = [0, 0]
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
    kd = 0 if totalKilled == 0 else float("inf") if totalLost == 0.0 else float(totalKilled)/float(totalLost)
    attackKd = 0 if currAttack[0] == 0 else float("inf") if currAttack[1] == 0.0 else float(currAttack[0])/float(currAttack[1])
    defendKd = 0 if currDefend[0] == 0 else float("inf") if currDefend[1] == 0.0 else float(currDefend[0])/float(currDefend[1])

    t.add_row([name, totalKilled, totalLost, "{:.2F}".format(kd),
        currAttack[0], currAttack[1], "{:.2F}".format(attackKd),
        currDefend[0], currDefend[1], "{:.2F}".format(defendKd) ])

print(t)
