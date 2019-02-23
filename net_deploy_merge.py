#!/usr/bin/python2.7
import sys
import time
import json
from napalm import get_network_driver


dcs_raw = 'dc.json'
dc_sel = str(raw_input('select dc (or type \"all\" is for all): '))
role_sel = str(raw_input('select role: '))
with open(dcs_raw, 'r') as dcs_file:
    dcs_db = json.load(dcs_file)

class NetNode:

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

    def node_view_users(self):
        users = self.node_driver.get_users()
        print(users)

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
    
    @staticmethod
    def node_select(dc_sel, role_sel, dcs_db):
        for k, v in dcs_db.items():
            for k1, v1 in v.items():
                if isinstance(v1, dict):
                    if dc_sel == 'all':
                        NetNode.node_select(dc_sel, role_sel, v1)
                        for k2, v2 in v1.items():
                            if k2.startswith(role_sel):
                                nodes_selected = v2.values()
                                return nodes_selected
                    if k1 == dc_sel:
                        NetNode.node_select(dc_sel, role_sel, v1)
                        for k2, v2 in v1.items():
                            if k2.startswith(role_sel):
                                nodes_selected = v2.values()
                                return nodes_selected


class NetCommit:

    def __init__(self):
        for i in NetNode.node_select(dc_sel, role_sel, dcs_db):
            self = NetNode(i)
            self.node_driver()
            self.node_open()
            self.node_merge()
            self.node_compare_config()
            self.node_decision()
            print("waiting before closing")
            time.sleep(30)
            self.node_close()


class NetView:

    def __init__(self):
        for i in NetNode.node_select(dc_sel, role_sel, dcs_db):
            self = NetNode(i)
            self.node_driver()
            self.node_rpc_timeout()
            self.node_open()
            self.node_view_users()
            self.node_close()


if __name__ == "__main__":
    NetView()
#    NetNode()
#    NetCommit()



sys.exit()
