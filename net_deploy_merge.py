#!/usr/bin/python2.7
import sys
import time
from napalm import get_network_driver

class Net_Node:
	def __init__(self, hostname, username='user', password='pass'):
		self.hostname = hostname
		self.username = username
		self.password = password

	def node_driver(self):
		driver = get_network_driver('junos')
		self.node_driver = driver(self.hostname, self.username, self.password)

	"""
	Default netconf rpc timeout is 30 seconds.
	This is not enough for srx cluster to commit the config.
	Increase it to avoid RpcTimeoutError or TimeoutExpiredError
	"""
	def node_rpc_timeout(self):
		self.node_driver.timeout = 300

	def node_open(self):
		self.node_driver.open()
		print("opening " + str(self.hostname))

	def node_merge(self):
		self.node_driver.load_merge_candidate(filename=sys.argv[1])

	def node_compare_config(self):
		print("listing changes below: ")
		diff = self.node_driver.compare_config()
		print(diff)

	def node_commit(self):
		print("committing " + str(self.hostname))
		self.node_driver.commit_config()

	def node_close(self):
		print("closing " + str(self.hostname))
		self.node_driver.close()

	def node_discard(self):
		self.node_driver.discard()

	def node_decision(self):
		change_decision = raw_input('commit or discard?: ')
		if change_decision == 'commit':
			print('got it, committing like a boss')
			self.node_commit()
		elif change_decision == 'discard':
			print('we cool, ain\'t bad playing it safe,  discarding like a boss')
			self.node_discard()
			print('see ya nerds, closing')
		else:
			print('something other')
			self.node_discard()
			raise sys.exit()

def main():
	"""
	In the initial commit, nodes are iterated over a simple list.
	upcoming commits will change that to json format split via nodes role in a DC
	"""
	optimus_prime = []
	megatron = ['node1', 'node2']
	for i in megatron:
		 n = Net_Node(i)
		 n.node_driver()
		 n.node_rpc_timeout()
		 n.node_open()
		 n.node_merge()
		 n.node_compare_config()
		 n.node_decision()
		 print("waiting before closing")
		 time.sleep(30)
		 n.node_close()

if __name__ == "__main__":
	main()

sys.exit()
