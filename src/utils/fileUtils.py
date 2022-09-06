## basic file operations

# interaction with operating system (read write files).
import os

def createFileIfNotExists(fileToCreateIfNotExists):
	# Seperate directory from filename.
	if "/" in fileToCreateIfNotExists:
		lastSlashPosition = fileToCreateIfNotExists.rfind("/")

		directoryName = fileToCreateIfNotExists[0:(lastSlashPosition)]
		if not os.path.exists(directoryName):
			os.makedirs(directoryName)
			os.chmod(directoryName, 0o775)

		if not os.path.exists(fileToCreateIfNotExists):
			os.mknod(fileToCreateIfNotExists)
			os.chmod(fileToCreateIfNotExists, 0o775)
	else:
		print("Cannot create a file without directory (pass filename containing filepath like \"path/to/file.txt\")")