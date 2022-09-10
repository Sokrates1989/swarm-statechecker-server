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

# BackupCheckItem from own models to use location independent.
import backupCheckItem as BackupCheckItem


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





	# Create or update backup check of a tool.
	# Pass backupCheckItem as parameter.
	def createOrUpdateBackupCheck(self, backupCheckItemToCreateOrUpdate):

		# Current time.
		now = int(time.time())

		# Does item already exist?
		backupCheckItem = self.getBackupCheckItemByName(backupCheckItemToCreateOrUpdate.name)
		if backupCheckItem == None:
			# Create new tool to check for.
			backupCheckItem = self.createNewBackupCheck(backupCheckItemToCreateOrUpdate)
		else:
			# Check if the token is the same.
			if backupCheckItem.token == backupCheckItemToCreateOrUpdate.token:
				# Update last time tool was up.
				backupCheckItem = self.updateBackupCheck(backupCheckItemToCreateOrUpdate)
			else:
				# token is invalid.
				return None
		return backupCheckItem

	# Get BackupCheckItem by its name.
	# Pass name as parameter.
	# Return is backupCheckItem with DB ID or None.
	def getBackupCheckItemByName(self, name):
		query = "SELECT ID, name, description, token, stateCheckFrequency_inMinutes, mostRecentBackupFile_creationDate, mostRecentBackupFile_hash, backupIsDownMessageHasBeenSent FROM checked_backups WHERE name=%s "
		val = (name, )
		self.mycursor.execute(query, val)
		myresult = self.mycursor.fetchone()

		# Did query retrieve valid backupCheckItem?
		backupCheckItem = None
		if (myresult != None):

			backupCheckItemHelper = {
				'ID': myresult[0],
				'name': myresult[1],
				'description': myresult[2],
				'token': myresult[3],
				'stateCheckFrequency_inMinutes': myresult[4],
				'mostRecentBackupFile_creationDate': myresult[5],
				'mostRecentBackupFile_hash': myresult[6],
				'backupIsDownMessageHasBeenSent': myresult[7]
			}

			backupCheckItem = BackupCheckItem.BackupCheckItem(
				backupCheckItemHelper["name"],
				backupCheckItemHelper["token"], 
				backupCheckItemHelper["stateCheckFrequency_inMinutes"], 
				backupCheckItemHelper["mostRecentBackupFile_creationDate"],
				backupCheckItemHelper["mostRecentBackupFile_hash"],
				backupCheckItemHelper["description"],
				backupCheckItemHelper["ID"],
				backupCheckItemHelper["backupIsDownMessageHasBeenSent"]
			)
		return backupCheckItem


	# Create a new stateCheck.
	# Pass backupCheckItem as parameter.
	def createNewBackupCheck(self, backupCheckItemToCreate):

		# Current time.
		now = int(time.time())

		# Does item already exist?
		backupCheckItem = self.getBackupCheckItemByName(backupCheckItemToCreate.name)
		if backupCheckItem == None:

			# Create new tool to check state of.
			# Execute insert query to create a new backup check item.
			insertSql = "INSERT INTO checked_backups (name, description, token, stateCheckFrequency_inMinutes, mostRecentBackupFile_creationDate, mostRecentBackupFile_hash) VALUES (%s, %s, %s, %s, %s, %s)"
			val = (backupCheckItemToCreate.name, backupCheckItemToCreate.description, backupCheckItemToCreate.token, backupCheckItemToCreate.stateCheckFrequency_inMinutes, backupCheckItemToCreate.mostRecentBackupFile_creationDate, backupCheckItemToCreate.mostRecentBackupFile_hash)
			self.mycursor.execute(insertSql, val)
			self.mydb.commit()

			# Return newly created user.
			return self.getBackupCheckItemByName(backupCheckItemToCreate.name)
		else:
			# Item already exists -> do nothing and return None.
			return None



	# Update backup state.
	# Returns updated stateItem.
	def updateBackupCheck(self, backupCheckItemToUpdate):

		# Check if the token is the same.
		backupCheckItem = self.getBackupCheckItemByName(backupCheckItemToUpdate.name)
		if backupCheckItem.token == backupCheckItemToUpdate.token:

			# Only update the item, if the hash changed.
			if backupCheckItem.mostRecentBackupFile_hash == backupCheckItemToUpdate.mostRecentBackupFile_hash:
				print ("hash did not change")
				return backupCheckItem
			else:
				sql = "UPDATE checked_backups SET description = %s, stateCheckFrequency_inMinutes = %s, mostRecentBackupFile_creationDate = %s, mostRecentBackupFile_hash = %s WHERE ID = %s"
				val = (
					backupCheckItemToUpdate.description, 
					backupCheckItemToUpdate.stateCheckFrequency_inMinutes, 
					backupCheckItemToUpdate.mostRecentBackupFile_creationDate, 
					backupCheckItemToUpdate.mostRecentBackupFile_hash, 
					backupCheckItem.ID
				)

				# Execute query.
				self.mycursor.execute(sql, val)
				self.mydb.commit()

				# Return updated item.
				return self.getBackupCheckItemByName(backupCheckItemToUpdate.name)

		else:
			# Token is invalid.
			return None



	# Update state of backupIsDownMessageHasBeenSent.
	# Pass backupCheckItemName and new state as parameter.
	def updateBackupIsDownMessageHasBeenSentState(self, backupCheckItemName, newBackupIsDownMessageHasBeenSentState):

		# Get the backupCheckItem.
		backupCheckItem = self.getBackupCheckItemByName(backupCheckItemName)

		# Current time.
		now = int(time.time())

		sql = "UPDATE checked_backups SET backupIsDownMessageHasBeenSent = %s WHERE ID = %s"
		val = (newBackupIsDownMessageHasBeenSentState, backupCheckItem.ID)

		# Execute query.
		self.mycursor.execute(sql, val)
		self.mydb.commit()

		# Return updated item.
		return self.getBackupCheckItemByName(backupCheckItem.name)

			
	# Stop checking backup state.
	# Pass backupCheckItem as parameter.
	def stopBackupCheck(self, backupCheckItemToDelete):

		# Verify correct token.
		backupCheckItem = self.getBackupCheckItemByName(backupCheckItemToDelete.name)
		if backupCheckItem != None and backupCheckItemToDelete.token == backupCheckItem.token:

			# Delete backup check.
			query = "DELETE FROM checked_backups WHERE ID=%s "
			val = (backupCheckItem.ID, )
			self.mycursor.execute(query, val)
			self.mydb.commit()

			return "Successfully stopped checking backup"
		else:
			return None




	# Get all backups to check.
	# Return is an associative array or an empty array.
	def getAllBackupsToCheck(self):
		query = "SELECT name FROM checked_backups ORDER BY ID"
		self.mycursor.execute(query)
		myresults = self.mycursor.fetchall()

		toolsToCheck = []
		for result in myresults:
			toolToCheck = self.getBackupCheckItemByName(result[0])
			toolsToCheck.append(toolToCheck)
		return toolsToCheck