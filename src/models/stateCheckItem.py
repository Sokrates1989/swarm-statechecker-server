## Model used to wrap crucial information about the tool to check.
## This model is only used for tools that are checked by sending alive messages via the API.

# Json model of a valid StateCheckItem to send to the API.
# {
#   "name": "Test",
#   "token": "IOdeFyatMDKyCUmVqtQkk4eGcnBYvvGp6aCakzj0ZdSBBtCfGrQvGn8RSbHuJO7RaI6jzGqDq2zmYNaYwY1NHUQJ7xCtPzblGt96",
#   "stateCheckFrequency_inMinutes": 60
# }

# Json model of a valid StateCheckItem with description to send to the API.
# {
#   "name": "Test",
#   "description": "Just a test tool to test some tests",
#   "token": "IOdeFyatMDKyCUmVqtQkk4eGcnBYvvGp6aCakzj0ZdSBBtCfGrQvGn8RSbHuJO7RaI6jzGqDq2zmYNaYwY1NHUQJ7xCtPzblGt96",
#   "stateCheckFrequency_inMinutes": 60
# }


class StateCheckItem:

    # Constructor.
    def __init__(self, name, token, stateCheckFrequency_inMinutes, description = "", ID = None, lastTimeToolWasUp = None, toolIsDownMessageHasBeenSent = 0):

        self.ID = ID
        self.name = name
        self.description = description
        self.token = token
        self.stateCheckFrequency_inMinutes = stateCheckFrequency_inMinutes
        self.lastTimeToolWasUp = lastTimeToolWasUp
        self.toolIsDownMessageHasBeenSent = toolIsDownMessageHasBeenSent