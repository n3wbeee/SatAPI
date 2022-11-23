from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import _thread
import uvicorn
from fastapi import FastAPI

app = FastAPI()

satState = [{
    "name": "AO-7",
    "reports": [{
            "status": "active",
            "count": 4,
            "reportState": "Heard JA2NLT PM94ex 2022-11-16 0:46-:59 UTC",
    }]
}
]

driver = webdriver.ChromiumEdge()
driver.get("https://www.amsat.org/status/")


@ app.get("/api/sat")
async def getSatState():
    return satState


def startAPIServer():
    uvicorn.run(app, host="localhost", log_level="info")


satCellList = []
satState_x = {}
if __name__ == "__main__":
    _thread.start_new_thread(startAPIServer, ())
    while True:
        numberDict = {}
        script = driver.find_element(By.CSS_SELECTOR, 'body > script').get_attribute('innerHTML')
        for text in script.split('tips.a'):
            try:
                satStateCode = int(text[0:7])
            except:
                continue
            else:
                satStateCode = str(satStateCode)
                numberDict['a' + satStateCode] = text[32:text.find("UTC\');") + 3].replace('<br>', ' ')

        for table in driver.find_elements(
                By.CSS_SELECTOR, 'body > center:nth-child(8) > table > tbody'):
            for row in table.find_elements(By.TAG_NAME, "tr"):
                for cell in row.find_elements(By.TAG_NAME, "td"):
                    if cell.text:
                        innerCode = cell.get_attribute('innerHTML')
                        n = int(innerCode.find('docTips.show'))
                        if n == -1:
                            n = int(innerCode.find('>', 2, -1))
                            p = int(innerCode.find('<', 2, -1))
                            satName = innerCode[n+1:p]
                        else:
                            outerCode = cell.get_attribute('outerHTML')
                            m = int(outerCode.find('bgcolor'))
                            if m != -1:
                                q = int(outerCode.find('"><a href'))
                                colorCode = outerCode[m + 9:q]
                                if colorCode == 'red':
                                    colorCode = 'No signal'
                                elif colorCode == '#4169E1':
                                    colorCode = 'Transponder/Repeater active'
                                elif colorCode == 'yellow':
                                    colorCode = 'Telemetry/Beacon only'
                                elif colorCode == 'orange':
                                    colorCode = 'Conflicting reports'
                                else:
                                    colorCode = 'ISS Crew (Voice) Active'
                            satCell = {"status": colorCode, "count": cell.text, "reportState": numberDict.get(innerCode[n+14:n+21], 'Not Found')}
                            satCellList.append(satCell)
                    else:
                        satCellList.append('NO Report')
                    satState_x = {"name": satName, "reports": satCellList}
                satState.append(satState_x)
                satCellList = []
        time.sleep(60)
