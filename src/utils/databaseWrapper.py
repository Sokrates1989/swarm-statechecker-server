### Class for any interaction with the DB.
### All write and read operations of DB should be done in this file/ class.

## Imports.
# database connection.
import mysql.connector
# file sytem operations.
import os
# For getting config.
import json
# To retrieve current timestamp.
import time

# Import own classes.
# Insert path to own stuff to allow importing them.
import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "..", "utils"))
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "..", "models"))

# StateCheckItem from own models to use location independent.
import stateCheckItem as StateCheckItem


class DatabaseWrapper:

	# Constructor.
	def __init__(self):

		# Get credentials for database from config file.
		config_file_pathAndName = os.path.join(os.path.dirname(__file__), "..", "..", "config.txt")
		config_file = open(config_file_pathAndName)
		config_array = json.load(config_file)

		# Database connection
		self.mydb = mysql.connector.connect(
			host=config_array["database"]["host"],
			user=config_array["database"]["user"],
			password=config_array["database"]["password"],
			database=config_array["database"]["database"],
			port=config_array["database"]["port"]
		)
		self.mycursor = self.mydb.cursor(buffered=True) # need to buffer to fix mysql.connector.errors.InternalError: Unread result found (https://stackoverflow.com/questions/29772337/python-mysql-connector-unread-result-found-when-using-fetchone)



	# Create or update state check of a tool.
	# Pass stateCheckItem as parameter.
	def createOrUpdateStateCheck(self, stateCheckItemToCreateOrUpdate):

		# Current time.
		now = int(time.time())

		# Does item already exist?
		stateCheckItem = self.getStateCheckItemByName(stateCheckItemToCreateOrUpdate.name)
		if stateCheckItem == None:
			# Create new tool to check for.
			stateCheckItem = self.createNewStateCheck(stateCheckItemToCreateOrUpdate)
		else:
			# Check if the token is the same.
			if stateCheckItem.token == stateCheckItemToCreateOrUpdate.token:
				# Update last time tool was up.
				stateCheckItem = self.indicateThatToolIsUp(stateCheckItem, stateCheckItemToCreateOrUpdate.description, stateCheckItemToCreateOrUpdate.stateCheckFrequency_inMinutes)
			else:
				# token is invalid.
				return None
		return stateCheckItem

	# Get StateCheckItem by its name.
	# Pass name as parameter.
	# Return is stateCheckItem with DB ID or None.
	def getStateCheckItemByName(self, name):
		query = "SELECT ID, name, description, token, stateCheckFrequency_inMinutes, lastTimeToolWasUp, toolIsDownMessageHasBeenSent FROM checked_tools WHERE name=%s "
		val = (name, )
		self.mycursor.execute(query, val)
		myresult = self.mycursor.fetchone()

		# Did query retrieve valid stateCheckItem?
		stateCheckItem = None
		if (myresult != None):

			stateCheckItemHelper = {
				'ID': myresult[0],
				'name': myresult[1],
				'description': myresult[2],
				'token': myresult[3],
				'stateCheckFrequency_inMinutes': myresult[4],
				'lastTimeToolWasUp': myresult[5],
				'toolIsDownMessageHasBeenSent': myresult[6]
			}

			stateCheckItem = StateCheckItem.StateCheckItem(
				stateCheckItemHelper["name"],
				stateCheckItemHelper["token"], 
				stateCheckItemHelper["stateCheckFrequency_inMinutes"], 
				stateCheckItemHelper["description"],
				stateCheckItemHelper["ID"],
				stateCheckItemHelper["lastTimeToolWasUp"],
				stateCheckItemHelper["toolIsDownMessageHasBeenSent"]
			)
		return stateCheckItem


	# Create a new stateCheck.
	# Pass stateCheckItem as parameter.
	def createNewStateCheck(self, stateCheckItemToCreate):

		# Current time.
		now = int(time.time())

		# Does item already exist?
		stateCheckItem = self.getStateCheckItemByName(stateCheckItemToCreate.name)
		if stateCheckItem == None:

			# Create new tool to check state of.
			# Execute insert query to create a new state check item.
			insertSql = "INSERT INTO checked_tools (name, description, token, stateCheckFrequency_inMinutes, lastTimeToolWasUp) VALUES (%s, %s, %s, %s, %s)"
			val = (stateCheckItemToCreate.name, stateCheckItemToCreate.description, stateCheckItemToCreate.token, stateCheckItemToCreate.stateCheckFrequency_inMinutes, now)
			self.mycursor.execute(insertSql, val)
			self.mydb.commit()

			# Return newly created user.
			return self.getStateCheckItemByName(stateCheckItemToCreate.name)
		else:
			# Item already exists -> do nothing and return None.
			return None



	# Update lastTimeToolWasUp.
	# Returns updated stateItem.
	def indicateThatToolIsUp(self, stateCheckItemToUpdate, description, stateCheckFrequency_inMinutes):

		# Check if the token is the same.
		stateCheckItem = self.getStateCheckItemByName(stateCheckItemToUpdate.name)
		if stateCheckItem.token == stateCheckItemToUpdate.token:

			# Current time.
			now = int(time.time())

			sql = "UPDATE checked_tools SET lastTimeToolWasUp = %s, description = %s, stateCheckFrequency_inMinutes = %s WHERE ID = %s"
			val = (now, description, stateCheckFrequency_inMinutes, stateCheckItemToUpdate.ID)

			# Execute query.
			self.mycursor.execute(sql, val)
			self.mydb.commit()

			# Return updated item.
			return self.getStateCheckItemByName(stateCheckItemToUpdate.name)

		else:
			# Token is invalid.
			return None



	# Update state of ToolIsDownMessageHasBeenSent.
	# Pass stateCheckItemName and new state as parameter.
	def updateToolIsDownMessageHasBeenSentState(self, stateCheckItemName, newToolIsDownMessageHasBeenSentState):

		# Get the stateCheckItem.
		stateCheckItem = self.getStateCheckItemByName(stateCheckItemName)

		# Current time.
		now = int(time.time())

		sql = "UPDATE checked_tools SET toolIsDownMessageHasBeenSent = %s WHERE ID = %s"
		val = (newToolIsDownMessageHasBeenSentState, stateCheckItem.ID)

		# Execute query.
		self.mycursor.execute(sql, val)
		self.mydb.commit()

		# Return updated item.
		return self.getStateCheckItemByName(stateCheckItem.name)

			
	# Stop checking state.
	# Pass stateCheckItem as parameter.
	def stopStateCheck(self, stateCheckItemToDelete):

		# Verify correct token.
		stateCheckItem = self.getStateCheckItemByName(stateCheckItemToDelete.name)
		if stateCheckItem != None and stateCheckItemToDelete.token == stateCheckItem.token:

			# Delete state check.
			query = "DELETE FROM checked_tools WHERE ID=%s "
			val = (stateCheckItem.ID, )
			self.mycursor.execute(query, val)
			self.mydb.commit()

			return "Successfully stopped checking state"
		else:
			return None




	# Get all tools to check.
	# Return is an associative array or an empty array.
	def getAllToolsToCheck(self):
		query = "SELECT name FROM checked_tools ORDER BY ID"
		self.mycursor.execute(query)
		myresults = self.mycursor.fetchall()

		toolsToCheck = []
		for result in myresults:
			toolToCheck = self.getStateCheckItemByName(result[0])
			toolsToCheck.append(toolToCheck)
		return toolsToCheck