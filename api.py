from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium import webdriver
import time
import _thread
import uvicorn
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi import Response

# TODO: Add a API function that can add data to the database
# TODO: Connect to db
# !!!   Performance not tested yet

app = FastAPI()  # Create a FastAPI instance
@app.get("/sat")
async def get_item(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return satState_json


# Template
satState = []


options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.ChromiumEdge(options=options)
driver.get("https://www.amsat.org/status/")


def startAPIServer():
    # Start the API server
    uvicorn.run(app, host="localhost", log_level="info")


if __name__ == "__main__":
    satCellList = []  # List of satellite cells
    satStateBuffer = {}  # Buffer of satellite state

    # Start the API server in a new thread
    _thread.start_new_thread(startAPIServer, ())

    while True:
        numberDict = {}
        script = driver.find_element(
            By.CSS_SELECTOR, 'body > script').get_attribute('innerHTML')  # Get the script
        for text in script.split('tips.a'):
            try:
                satStateCode = int(text[0:7])  # Get the satellite state code
            except:
                continue
            else:
                satStateCode = str(satStateCode)  # Convert to string
                numberDict['a' + satStateCode] = text[32:
                                                      text.find("UTC\');") + 3].replace('<br>', ' ')

        for table in driver.find_elements(
                By.CSS_SELECTOR, 'body > center:nth-child(8) > table > tbody'):  # Get the table
            for row in table.find_elements(By.TAG_NAME, "tr"):  # Get the row
                satName = ""
                for cell in row.find_elements(By.TAG_NAME, "td"):  # Get the cell
                    if cell.text:  # If the cell is not empty
                        if cell.text.isdigit():  # If the cell is a number
                            colorCode = ""
                            outerCode = cell.get_attribute('outerHTML')
                            colorLower = int(outerCode.find('bgcolor'))
                            if colorLower != -1:
                                colorUpper = int(outerCode.find('"><a href'))
                                colorCode = outerCode[colorLower +
                                                      9: colorUpper]
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

                                innerCode = cell.get_attribute('innerHTML')
                                lower = int(innerCode.find("('", 2, -1))
                                upper = int(innerCode.find('<', 2, -1))
                                satCell = {"status": colorCode, "count": cell.text, "reportState": numberDict.get(
                                    innerCode[lower + 2: lower + 9], 'Not Found')}
                                satCellList.append(satCell)
                        else:  # If the cell is a satellite name
                            satName = cell.text
                    else:
                        satCellList.append('NO Report')  # If the cell is empty
                    # Create a satellite state buffer
                    satStateBuffer = {"name": satName, "reports": satCellList}

                # Add the satellite state buffer to the satellite state list
                satState.append(satStateBuffer)
                satCellList = []  # Clear the satellite cell list
        satState.pop(0)
        t = time.ctime()
        satState_dict = {"data": satState, "time": t}
        satState = []
        satState_json = jsonable_encoder(satState_dict)
        time.sleep(0)
        del satState_dict
