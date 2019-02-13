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

optimus_prime = ['node1', 'node2']
megatron = ['node3', 'node4']


class Net_Commit:

    def __init__(self):
        for i in self.group_decision():
            self = Net_Node(i)
            self.node_driver()
            self.node_open()
            self.node_merge()
            self.node_compare_config()
            self.node_decision()
            print("waiting before closing")
            time.sleep(30)
            self.node_close()

    def group_decision(self):
        self = []
        print('1: ' + str(optimus_prime))
        print('2: ' + str(megatron))
        group_input = raw_input('choose from 1 or 2: ')
        if group_input == '1':
            self = optimus_prime
        elif group_input == '2':
            self = megatron
        return self

if __name__ == "__main__":
    Net_Commit()

sys.exit()
