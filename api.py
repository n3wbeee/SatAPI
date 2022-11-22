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
        for table in driver.find_elements(
                By.CSS_SELECTOR, 'body > center:nth-child(8) > table > tbody'):
            for row in table.find_elements(By.TAG_NAME, "tr"):
                for cell in row.find_elements(By.TAG_NAME, "td"):
                    if cell.text:
                        innerCode = cell.get_attribute('innerHTML')
                        n = int(innerCode.find('docTips.show'))
                        if n==-1:
                            n = int(innerCode.find('>', 2, -1))
                            p = int(innerCode.find('<', 2, -1))
                            satName = innerCode[n+1:p]
                        else:
                            satCell = innerCode[n+14:n+21]
                            satCellList.append(satCell)
                    else:
                        continue
                    satState_x = {"name": satName, "reports": satCellList}
                satState.append(satState_x)
                satCellList = []
        print(satState)
        break
exitCode = input("PUSH ANY KEY TO EXIT")
