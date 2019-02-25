#!/usr/bin/python2.7
import sys
import time
import json
from napalm import get_network_driver


dcs_raw = 'dc.json'
#dc_sel = str(raw_input('select dc (or type \"all\" is for all): '))
#role_sel = str(raw_input('select role: '))
with open(dcs_raw, 'r') as dcs_file:
    dcs_db = json.load(dcs_file)

class NetNode:

    def __init__(self, hostname, username='vMx', password=''):
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
        self.node_driver.close()

    def node_discard(self):
        self.node_driver.discard()

    def node_view_users(self):
        users = self.node_driver.get_users()
        print(users)

    def node_bgp_status(self):
        bgp_summary = self.node_driver.get_bgp_neighbors()
        with open('status_page_bgp.json', 'w') as sp_bgp_f_json:
            for k, v in bgp_summary.items():
                for k1, v1 in v['peers'].items():
                    bgp_summary_l = []
                    bgp_summary_d = {}
                    bgp_summary_d[self.hostname] = {}
                    bgp_summary_d[self.hostname][k] = {}
                    #bgp_summary_d['router'] = self.hostname
                    #bgp_summary_d[self.hostname]['vrouter'] = k
                    bgp_summary_d[self.hostname][k]['bgp_neigh'] = k1
                    bgp_summary_d[self.hostname][k]['bgp_neigh_desc'] = v1['description']
                    bgp_summary_d[self.hostname][k]['bgp_neigh_uptime'] = v1['uptime']
                    bgp_summary_l.append(bgp_summary_d)
                    json.dump(bgp_summary_l, sp_bgp_f_json, separators=(',', ':'), indent=4, sort_keys=True)
                    #sp_bgp_f_json.write('\n')
        
        with open('status_page_bgp.txt', 'w') as sp_bgp_f_txt:
            for k, v in bgp_summary.items():
                for k1, v1 in v['peers'].items():
                    bgp_summary_list = []
                    # bgp_summary_d = {}
                    # bgp_summary_d[self.hostname] = {}
                    # bgp_summary_d[self.hostname][k] = {}
                    # #bgp_summary_d['router'] = self.hostname
                    # #bgp_summary_d[self.hostname]['vrouter'] = k
                    # bgp_summary_d[self.hostname][k]['bgp_neigh'] = k1
                    # bgp_summary_d[self.hostname][k]['bgp_neigh_desc'] = v1['description']
                    # bgp_summary_d[self.hostname][k]['bgp_neigh_uptime'] = v1['uptime']
                    # json.dump(bgp_summary_d, sp_bgp_f, separators=(',', ':'), indent=4, sort_keys=True)
                    # sp_bgp_f_txt.write('\n')

                    # sp_bgp_f.write(json.dumps((bgp_summary_d, indent=4)))
                    # sp_bgp_f.write('\n' + str((k, k1, v1['description'], v1['uptime'])))
                    bgp_summary_list.append(str(self.hostname))
                    bgp_summary_list.append(k)
                    bgp_summary_list.append(str(k1))
                    bgp_summary_list.append(str(v1['description']))
                    bgp_summary_list.append(v1['uptime'])
                    sp_bgp_f_txt.write(str(bgp_summary_list) + '\n')
                    # print(bgp_summary_list)
                    
                    # print(k, str(k1), str(v1['description']), str(v1['uptime']))
                    # sp_bgp_f.write(str(k) + ", " + str(k1) + ", " + str(v1['description']) + ", " + str(v1['uptime']) + '\n')
                    # sp_bgp_f.write(str(k, str(k1), str(v1['description']), str(v1['uptime'])))

    @staticmethod
    def all_bgp_nodes():
        router_list = []
        b_nodes = dcs_db['DCs'].keys()
        for i in NetNode.node_select('DC1', 'router', dcs_db):
            router_list.append(i)
        for j in NetNode.node_select('DC2', 'router', dcs_db):
            router_list.append(j)
        return router_list



        
        # for v in dcs_db.values():
        #     for k1, v1 in v.items():
        #         for k2, v2 in v1.items():
        #             print(k2, v2)
        #         #return v1['router'].values()
            #print(k)
         #   for v1 in v[k]['router'].values():
                #print(v1)
            #print(v['DC1']['router'])
            # print(v)
            #for k1, v1 in v.items():
                #print(k1)
                #print(v1)
                #print(v1['DC2']['router']).values()
             #   return v1["router"].values()

    def node_arp_table(self):
        arp_ip_d = {}
        arp_table = self.node_driver.get_arp_table()
        with open('status_page_arp', 'w') as sp_arp_f:
            for arp_ip in arp_table:
                arp_ip_d['ip'] = arp_ip['ip']
                arp_ip_d['mac'] = arp_ip['mac']
                sp_arp_f.write(str(arp_ip_d) + '\n')

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
        for v in dcs_db.values():
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

class NetStatus:

    def __init__(self):
        for i in NetNode.all_bgp_nodes():
            print(i)
            self = NetNode(i)
            print(i)
            self.node_driver()
            self.node_rpc_timeout()
            self.node_open()
            self.node_bgp_status()
            self.node_arp_table()
            self.node_close()

if __name__ == "__main__":
    NetStatus()

sys.exit()
