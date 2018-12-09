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

	def node_open(self):
		self.node_driver.open()
		print("opening " + str(self.hostname))

	def node_merge(self):
		"""
		change filename to either sys argv or input on the next version,
		consider roles/section of the change being made
		"""
		self.node_driver.load_merge_candidate(filename='config_goes_here')

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
		 n.node_open()
		 n.node_merge()
		 n.node_compare_config()
		 n.node_commit()
		 print("waiting before closing")
		 time.sleep(30)
		 n.node_close()

if __name__ == "__main__":
	main()

sys.exit()
