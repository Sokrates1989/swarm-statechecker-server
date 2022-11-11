from typing import Union

from fastapi import FastAPI, Response, status
from pydantic import BaseModel

# Import own classes.
# Insert path to own stuff to allow importing them.
import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "src/", "utils"))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "src/", "models"))

# Database Connection.
import databaseWrapper as DatabaseWrapper

# Checking credentials with hash utils.
import hashUtils

# StateCheckItem from own models to use location independent.
import stateCheckItem as StateCheckItem

# BackupCheckItem from own models to use location independent.
import backupCheckItem as BackupCheckItem

# StateCheckItem as pydantic model to use with fastAPI.
# To unify usage, this model should be converted to StateCheckItem asap.
# @see convertPydanticModelToStateCheckItem().
class StateCheckItem_pydantic(BaseModel):
    name: str
    description: Union[str, "None"] = "None"
    token: str
    hashedString: Union[str, "None"] = "None"
    autoHealCommand: Union[str, "None"] = "None"
    stateCheckFrequency_inMinutes: int



# BackupCheckItem as pydantic model to use with fastAPI.
# To unify usage, this model should be converted to BackupCheckItem asap.
# @see convertPydanticModelToBackupCheckItem().
class BackupCheckItem_pydantic(BaseModel):
    name: str
    description: Union[str, "None"] = "None"
    token: str
    stateCheckFrequency_inMinutes: int
    mostRecentBackupFile_creationDate: str
    mostRecentBackupFile_hash: str


# Instantiate Fast API.
app = FastAPI()

@app.get("/")
async def root_get():
    return {"message": "https://github.com/Sokrates1989/stateChecker-client"}


# Start checking the availability of a new tool or update the last time the tool has been available.
@app.post("/v1/statecheck")
async def statecheck(stateCheckItem_pydantic: StateCheckItem_pydantic, response: Response):
    stateCheckItem = convertPydanticModelToStateCheckItem(stateCheckItem_pydantic)
    dbWrapper = DatabaseWrapper.DatabaseWrapper()
    stateCheckItem = dbWrapper.createOrUpdateStateCheck(stateCheckItem)
    if stateCheckItem == None:
        response.status_code = 401
        return {"message": "invalid token"}
    else:
        return stateCheckItem

# Stop checking the availablity of a watched tool.
@app.post("/v1/statecheck/stop")
async def stop_statecheck(stateCheckItem_pydantic: StateCheckItem_pydantic, response: Response):
    stateCheckItem = convertPydanticModelToStateCheckItem(stateCheckItem_pydantic)
    dbWrapper = DatabaseWrapper.DatabaseWrapper()
    stateCheckItem = dbWrapper.stopStateCheck(stateCheckItem)
    if stateCheckItem == None:
        response.status_code = 401
        return {"message": "invalid token"}
    else:
        return stateCheckItem



# Start checking a backup or update a backup check.
@app.post("/v1/backupcheck")
async def backupcheck(backupCheckItem_pydantic: BackupCheckItem_pydantic, response: Response):
    backupCheckItem = convertPydanticModelToBackupCheckItem(backupCheckItem_pydantic)
    dbWrapper = DatabaseWrapper.DatabaseWrapper()
    backupCheckItem = dbWrapper.createOrUpdateBackupCheck(backupCheckItem)
    if backupCheckItem == None:
        response.status_code = 401
        return {"message": "invalid token"}
    else:
        return backupCheckItem

# Stop checking the availablity of a watched tool.
@app.post("/v1/backupcheck/stop")
async def stop_backupcheck(backupCheckItem_pydantic: BackupCheckItem_pydantic, response: Response):
    backupCheckItem = convertPydanticModelToBackupCheckItem(backupCheckItem_pydantic)
    dbWrapper = DatabaseWrapper.DatabaseWrapper()
    backupCheckItem = dbWrapper.stopBackupCheck(backupCheckItem)
    if backupCheckItem == None:
        response.status_code = 401
        return {"message": "invalid token"}
    else:
        return backupCheckItem



# Converts pydantic StateCheckItem_pydantic to StateCheckItem.
def convertPydanticModelToStateCheckItem(stateCheckItem_pydantic: StateCheckItem_pydantic):

    # Ensure description is set.
    if stateCheckItem_pydantic.description == None:
        stateCheckItem_pydantic.description = ""

    stateCheckItem = StateCheckItem.StateCheckItem(
        stateCheckItem_pydantic.name, 
        stateCheckItem_pydantic.token, 
        stateCheckItem_pydantic.stateCheckFrequency_inMinutes, 
        stateCheckItem_pydantic.description
        )

    # Set hashedString if set.
    if stateCheckItem_pydantic.hashedString != None and stateCheckItem_pydantic.hashedString != "None":
        stateCheckItem.setHashedString(stateCheckItem_pydantic.hashedString)

    # Set autoHealCommand if set.
    if stateCheckItem_pydantic.autoHealCommand != None and stateCheckItem_pydantic.autoHealCommand != "None":
        stateCheckItem.setAutoHealCommand(stateCheckItem_pydantic.autoHealCommand)

    return stateCheckItem



# Converts pydantic BackupCheckItem_pydantic to BackupCheckItem.
def convertPydanticModelToBackupCheckItem(backupCheckItem_pydantic: BackupCheckItem_pydantic):

    # Ensure description is set.
    if backupCheckItem_pydantic.description == None:
        backupCheckItem_pydantic.description = ""

    backupCheckItem = BackupCheckItem.BackupCheckItem(
        backupCheckItem_pydantic.name,
        backupCheckItem_pydantic.token, 
        backupCheckItem_pydantic.stateCheckFrequency_inMinutes, 
        backupCheckItem_pydantic.mostRecentBackupFile_creationDate, 
        backupCheckItem_pydantic.mostRecentBackupFile_hash, 
        backupCheckItem_pydantic.description
        )
    return backupCheckItem