## Utilities to get states of tools, that are being checked.

# For getting current timestamp.
import time

# For making POST / GET requests.
import requests

# For file operations with operating system.
import os

# For creating files.
import fileUtils

# Path to messageSentStates of custom checks.
messageSentStatesDirectory = os.path.join(os.path.dirname(__file__), "..", "..", "messageSentStates/")

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
	toolStateItems_custom = getToolStates_custom()
	toolStateItems = toolStateItems_api + toolStateItems_custom
	for toolStateItem in toolStateItems:

			# Is the tool up?
			if toolStateItem.toolIsUp == False:
				# Tool is down.
				toolStatesMessage += "Tool <b>" + str(toolStateItem.name) + "</b> is <b>DOWN!</b>"
			else:
				# Tool is up.
				toolStatesMessage += "Tool <b>" + str(toolStateItem.name) + "</b> is <b>UP!</b>"

			# Add description and statusMessage if not empty and spaces to end of message.
			toolStatesMessage += "" if toolStateItem.description == "" else "\n" + str(toolStateItem.description)
			toolStatesMessage += "" if toolStateItem.statusMessage == "" or toolStateItem.statusMessage == "OK" else "\n" + str(toolStateItem.statusMessage)
			toolStatesMessage += "\n\n"

	return toolStatesMessage




# Get states of tools that are being checked manually from here.
# Returns Array of ToolStateItems. See models for further information.
def getToolStates_custom():

	# Array of ToolStateItems.
	toolStateItems = []

	# Check website states for felicitas wisdom.
	urls = [
		"https://felicitas-wisdom.com",
		"http://felicitas-wisdom.com",
		"https://www.felicitas-wisdom.com",
		"http://www.felicitas-wisdom.com",
		"https://telegram.felicitas-wisdom.com",
		"http://telegram.felicitas-wisdom.com",
		"http://wtf.felicitas-wisdom.com",
	]
	toolStateItems += getToolStates_websites(urls)
	
	# Return states of tools checked by the API.
	return toolStateItems



# Get states of websites.
# Returns Array of ToolStateItems. See models for further information.
def getToolStates_websites(urls):

	# Array of ToolStateItems.
	toolStateItems = []

	# Check all website urls.
	for url in urls: 

		# Check website states.
		fileNameForMessageSentState = fileUtils.getValidFileNameForString(url, "txt")
		messageSentStateFile = os.path.join(messageSentStatesDirectory, fileNameForMessageSentState)
		fileUtils.createFileIfNotExists(messageSentStateFile)
		messageSentState = fileUtils.readStringFromFile(messageSentStateFile)
		if messageSentState == "True":
			messageSentState = True
		else:
			messageSentState = False

		# Try to call website.
		try:
			x = requests.post(url)

			# Add state of tool to return array.
			toolStateItem = ToolStateItem.ToolStateItem(
				url,
				True if x.status_code == 200 else False, # Tool is up boolean value.
				messageSentState
			)
			toolStateItem.setStatusMessage(x.reason)
			toolStateItem.indicateThatToolIsCustom()
			toolStateItems.append(toolStateItem)
		except Exception as e:
			# Add state of tool to return array.
			toolStateItem = ToolStateItem.ToolStateItem(
				url,
				False, # Tool is up boolean value.
				messageSentState
			)
			toolStateItem.setStatusMessage("An Error was thrown trying to make request")
			toolStateItem.indicateThatToolIsCustom()
			toolStateItems.append(toolStateItem)
		
	
	# Return states of tools checked by the API.
	return toolStateItems


# Write state of sent message to file.
def writeMessageHasBeenSentStateToFile(toolStateItem, newState):
	fileNameForMessageSentState = fileUtils.getValidFileNameForString(toolStateItem.name, "txt")
	messageSentStateFile = os.path.join(messageSentStatesDirectory, fileNameForMessageSentState)
	fileUtils.createFileIfNotExists(messageSentStateFile)
	fileUtils.overwriteContentOfFile(messageSentStateFile, newState)