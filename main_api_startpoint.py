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

# StateCheckItem from own models to use location independent.
import stateCheckItem as StateCheckItem

# StateCheckItem as pydantic model to use with fastAPI.
# To unify usage, this model should be converted to StateCheckItem asap.
# @see convertPydanticModelToStateCheckItem().
class StateCheckItem_pydantic(BaseModel):
    name: str
    description: Union[str, "None"] = "None"
    token: str
    stateCheckFrequency_inMinutes: int

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
    return stateCheckItem