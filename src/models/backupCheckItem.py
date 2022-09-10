## Model used to wrap crucial information about the backup to check.
## This model is only used for backups that are checked by sending their most current file and its representating hash.

# Json model of a valid BackupCheckItem to send to the API.
# {
#   "name": "TestBackup",
#   "token": "IOdeFyatMDKyCUmVqtQkk4eGcnBYvvGp6aCakzj0ZdSBBtCfGrQvGn8RSbHuJO7RaI6jzGqDq2zmYNaYwY1NHUQJ7xCtPzblGt96",
#   "stateCheckFrequency_inMinutes": 60,
#   "mostRecentBackupFile_creationDate": "unixTimeStamp",
#   "mostRecentBackupFile_hash": "hashOfMostRecentbackupFile"
# }

# Json model of a valid BackupCheckItem with description to send to the API.
# {
#   "name": "TestBackup",
#   "description": "Just a test backup to test some backups",
#   "token": "IOdeFyatMDKyCUmVqtQkk4eGcnBYvvGp6aCakzj0ZdSBBtCfGrQvGn8RSbHuJO7RaI6jzGqDq2zmYNaYwY1NHUQJ7xCtPzblGt96",
#   "stateCheckFrequency_inMinutes": 60,
#   "mostRecentBackupFile_creationDate": "unixTimeStamp",
#   "mostRecentBackupFile_hash": "hashOfMostRecentbackupFile"
# }


class BackupCheckItem:

	# Constructor.
	def __init__(self, name, token, stateCheckFrequency_inMinutes, mostRecentBackupFile_creationDate, mostRecentBackupFile_hash, description = "", ID = None, backupIsDownMessageHasBeenSent = 0):

		self.ID = ID
		self.name = name
		self.description = description
		self.token = token
		self.stateCheckFrequency_inMinutes = stateCheckFrequency_inMinutes
		self.mostRecentBackupFile_creationDate = mostRecentBackupFile_creationDate
		self.mostRecentBackupFile_hash = mostRecentBackupFile_hash
		self.backupIsDownMessageHasBeenSent = backupIsDownMessageHasBeenSent