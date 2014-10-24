class BotLayer:

	def __init__(self):
		pass

	def pick_starting_regions(self, info, input):
		raise NotImplementedError('this is an abstract class')

	def place_troops(self, info, input):
		raise NotImplementedError('this is an abstract class')

	def attack_transfer(self, info, input):
		raise NotImplementedError('this is an abstract class')