## Utilities to get states of tools, that are being checked.

# For getting current timestamp.
import time

# Database connection.
import databaseWrapper as DatabaseWrapper

# ToolStateItem from own models to use location independent.
# Used to wrap state information about the tools to check.
import toolStateItem as ToolStateItem

# Get states of tools that are being checked by sending their own alive message to api.
# Returns Array of ToolStateItems. See models for further information.
def getToolStates_api():

	# Array of ToolStateItems.
	toolStateItems = []

	# Database connection.
	dbWrapper = DatabaseWrapper.DatabaseWrapper()

	# Did all tools send a state info within desired timespan?
	now = int(time.time())
	allToolsToCheck = dbWrapper.getAllToolsToCheck()
	if allToolsToCheck: 
		for toolToCheck in allToolsToCheck:

			# Has the state info been sent within the desired amount of time?
			if int(toolToCheck.lastTimeToolWasUp) + int(toolToCheck.stateCheckFrequency_inMinutes) * 65 < now:
				
				# No valid state check withing desired timespan.

				# Add state of tool to return array.
				toolStateItem = ToolStateItem.ToolStateItem(
					toolToCheck.name,
					False, # Tool is up boolean value.
					toolToCheck.toolIsDownMessageHasBeenSent,
					toolToCheck.description
				)
				toolStateItems.append(toolStateItem)


			else:
				
				# There is a valid state check withing desired timespan.

				# Add state of tool to return array.
				toolStateItem = ToolStateItem.ToolStateItem(
					toolToCheck.name,
					True, # Tool is up boolean value.
					toolToCheck.toolIsDownMessageHasBeenSent,
					toolToCheck.description
				)
				toolStateItems.append(toolStateItem)

	# Return states of tools checked by the API.
	return toolStateItems




# Get message for tool states to write in state message.
def getToolStatesMessage():

	# The message to return.
	toolStatesMessage = ""

	# Array of ToolStateItems.
	toolStateItems_api = getToolStates_api()
	for toolStateItem in toolStateItems_api:

			# Is the tool up?
			if toolStateItem.toolIsUp == False:
				
				# Tool is down.
				toolStatesMessage += "Tool <b>" + str(toolStateItem.name) + "</b> is <b>DOWN!</b> \n" + str(toolStateItem.description)

			else:
				
				# Tool is up.
				toolStatesMessage += "Tool <b>" + str(toolStateItem.name) + "</b> is <b>UP!</b> \n" + str(toolStateItem.description)

			# Add space to end of message.
			toolStatesMessage += "\n\n"

	return toolStatesMessage
