# Model used to wrap information about the states of the tools to check.

class ToolStateItem:

	# Constructor.
	def __init__(self, name, toolIsUp, toolIsDownMessageHasBeenSent, description = ""):

		# Convert toolIsDownMessageHasBeenSent to boolean.
		if toolIsDownMessageHasBeenSent == 0:
			toolIsDownMessageHasBeenSent = False
		if toolIsDownMessageHasBeenSent == 1:
			toolIsDownMessageHasBeenSent = True

		# Convert toolIsUp to boolean.
		if toolIsUp == 0:
			toolIsUp = False
		if toolIsUp == 1:
			toolIsUp = True

		# Ensure descriptions is not None.
		if description == None or description == "None" :
			description = ""

		self.name = name
		self.description = description
		self.toolIsUp = toolIsUp
		self.toolIsDownMessageHasBeenSent = toolIsDownMessageHasBeenSent
		self.statusMessage = ""
		self.isCustomCheck = False


	# Add statusMessage.
	def setStatusMessage(self, statusMessage):
		self.statusMessage = statusMessage


	# Indicate, that checked tool is a custom check.
	def indicateThatToolIsCustom(self):
		self.isCustomCheck = True