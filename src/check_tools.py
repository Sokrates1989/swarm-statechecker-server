## Execute this file to test if tools are up and running.

# Api for listening to bot commands.
import telebot
import time

# To get config json.
import json

# Be able to write trace to logfile.
import traceback

# Import own classes.
# Insert path to utils to allow importing them.
import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "utils"))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "models"))
import logger as Logger
import databaseWrapper as DatabaseWrapper
# Utils for getting state of tools.
import stateCheckUtils
import stringUtils

## Initialize vars.

# Get config.
config_file_pathAndName = os.path.join(os.path.dirname(__file__), "..", "config.txt")
config_file = open(config_file_pathAndName)
config_array = json.load(config_file)

# Instantiate classes.
# Database connection.
dbWrapper = DatabaseWrapper.DatabaseWrapper()
# Logger.
logger = Logger.Logger("check_tools")

# Initialize bots.
botToken = config_array["telegram"]["botToken"]
bot = telebot.TeleBot(botToken, parse_mode="HTML")
errorChatID = config_array["telegram"]["errorChatID"]
infoChatID = config_array["telegram"]["infoChatID"]


# Handles error exceptions (log and info to admin).
def handleCommandException(exceptionLocationAndAdditionalInformation, exception):
	# Log error.
	errorLogText = exceptionLocationAndAdditionalInformation + " " + str(exception)
	# Add traceback to logfile.
	traceOfError = traceback.format_exc() 
	logger.logError(str(traceOfError) + "\n" + errorLogText)

	# Send error message to admin telegram chat, if intended.
	bot.send_message(errorChatID, errorLogText)




# Info, that checking schedule is still taking place (log and info to admin).
def infoCheckingToolsIsWorking(justStartedChecking=False):

	# Create info text.
	infoLogText = "<b><u>Tools are being checked.</u></b>"
	if justStartedChecking:
		infoLogText += "\nJust (re-)started checking tools.\n\nAbout every " + str(adminMessageEvery_desiredMinutes) + " minutes a status message should be send, to verify that this program is still working correctly."
	else:
		infoLogText += "\n\nThis is an information to ensure, that the program is working correctly.\n\nThis message should show up again in " + str(adminMessageEvery_desiredMinutes) + " minutes, verifying that this program is still working correctly."
	infoLogText +=  "\nIf not -> Try to restart this program and take a look at the logs."

	# Add status message of checked tools.
	infoLogText += "\n\n" + stateCheckUtils.getToolStatesMessage()

	# Log information.
	logger.logInformation(infoLogText)

	# Send message to admin telegram chat.
	# Does message have to be split?
	if len(infoLogText) > 4096:

		# Split message.
		individualMessages = stringUtils.splitLongTextIntoWorkingMessages(infoLogText)

		# Send messages.
		for individualMessage in individualMessages:
			bot.send_message(infoChatID, individualMessage)
		
			
	else:
		# Message does not have to be split.
		bot.send_message(infoChatID, infoLogText)
	



## Check whether a scheduled countdown has to be sent.

# Only print every xth time, that we are still checking.
printEvery = 100

# Status message to admin chat, that tool is up.
adminMessageEvery_desiredMinutes = int(config_array["telegram"]["adminStatusMessage_everyXMinutes"])
adminMessageEvery_offsetPercentageCalculatingProcessionTime = float(config_array["telegram"]["adminStatusMessage_operationTime_offsetPercentage"])
adminMessageEvery_calculatedOffset = int(adminMessageEvery_desiredMinutes - (adminMessageEvery_desiredMinutes * adminMessageEvery_offsetPercentageCalculatingProcessionTime / 100))
# Avoid zero devision error.
if adminMessageEvery_calculatedOffset == 0:
	adminMessageEvery_calculatedOffset = 1

i = 0
print("checking ...")
infoCheckingToolsIsWorking(True)
while True:
	try:
		## Info that checking of schedule is still taking place.

		# Increment counter.
		i = i + 1

		# Output to console.
		if (i%printEvery == 0):
			print("checking (" + str(i) + ") ...")

		# Send message to admin chat.
		if (i%adminMessageEvery_calculatedOffset == 0):
			infoCheckingToolsIsWorking()

		# Get states of tools.
		toolStateItems_api = stateCheckUtils.getToolStates_api()
		toolStateItems_custom = stateCheckUtils.getToolStates_custom()
		toolStateItems = toolStateItems_api + toolStateItems_custom

		# Check the states of the tools.
		for toolStateItem in toolStateItems:

			# Is the tool up?
			if toolStateItem.toolIsUp == False:
				
				# Tool is down.

				# Has the error message already been sent?
				if toolStateItem.toolIsDownMessageHasBeenSent == False:

					# The error message has not been sent yet.
					# Output info.
					print ("Found tool, that is is down and message has not been sent yet..")
					print (toolStateItem.name)
					print ("sending mesage now..")

					# Indicate, that tool is down message has been sent.
					if toolStateItem.isCustomCheck == True:
						stateCheckUtils.writeMessageHasBeenSentStateToFile(toolStateItem, True)
					else:
						# Indicate to DB, that message has been sent.
						dbWrapper.updateToolIsDownMessageHasBeenSentState(toolStateItem.name, 1)
					
					# Send the message to the error message channel.
					toolStateItemIsDownMsg = "Your tool is <b>DOWN!</b> \n\n<b>" + str(toolStateItem.name) + "</b>"
					toolStateItemIsDownMsg += "" if toolStateItem.description == "" else "\n" + str(toolStateItem.description)
					toolStateItemIsDownMsg += "" if toolStateItem.statusMessage == "" or toolStateItem.statusMessage == "OK" else "\n" + str(toolStateItem.statusMessage)
					bot.send_message(errorChatID, toolStateItemIsDownMsg )


			else:
				
				# Tool is up.

				# Has there been an error message before ?
				if toolStateItem.toolIsDownMessageHasBeenSent == True:

					# There has been an error message recently.
					# Output info.
					print ("Found tool, that is up again..")
					print (toolStateItem.name)
					print ("sending mesage now..")

					# Indicate, that tool is down message has been sent.
					if toolStateItem.isCustomCheck == True:
						stateCheckUtils.writeMessageHasBeenSentStateToFile(toolStateItem, False)
					else:
						# Indicate to DB, that message has been sent.
						dbWrapper.updateToolIsDownMessageHasBeenSentState(toolStateItem.name, 0)
					
					# Send the message to the error message channel.
					toolStateItemIsUpAgainMsg = "Your tool is <b>UP AGAIN!</b> \n\n<b>" + str(toolStateItem.name) + "</b>"
					toolStateItemIsUpAgainMsg += "" if toolStateItem.description == "" else "\n" + str(toolStateItem.description)
					toolStateItemIsUpAgainMsg += "" if toolStateItem.statusMessage == "" or toolStateItem.statusMessage == "OK" else "\n" + str(toolStateItem.statusMessage)
					bot.send_message(errorChatID, toolStateItemIsUpAgainMsg )


		# Sleep 60 seconds.
		time.sleep(60)

	except Exception as e:
		handleCommandException("An Error occured while checking schedule: ", str(e))

		# Sleep 60 seconds.
		time.sleep(60)