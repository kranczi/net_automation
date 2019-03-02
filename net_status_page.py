#!/usr/bin/python2.7
import sys
import pprint
import time
import json
from napalm import get_network_driver


dcs_raw = 'dc.json'
with open(dcs_raw, 'r') as dcs_file:
    dcs_db = json.load(dcs_file)

class NetNode:

    def __init__(self, hostname, username='user', password='password'):
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
        bgp_ext = {}
        bgp_summary = self.node_driver.get_bgp_neighbors()
        for k, v in bgp_summary.items():
            # pprint.pprint(bgp_summary.items())
            for k1, v1 in v['peers'].items():
                # pprint.pprint(v['peers'].items())
                bgp_summary_d = {}
                bgp_summary_d[self.hostname] = {}
                bgp_summary_d[self.hostname][k] = {}
                #bgp_summary_d['router'] = self.hostname
                #bgp_summary_d[self.hostname]['vrouter'] = k
                bgp_summary_d[self.hostname][k]['bgp_neigh'] = k1
                bgp_summary_d[self.hostname][k]['bgp_neigh_desc'] = v1['description']
                bgp_summary_d[self.hostname][k]['bgp_neigh_uptime'] = v1['uptime']
                yield bgp_summary_d

                # print(bgp_summary_d)
                # bgp_summary_d
                #print(bgp_summary_d)
        # bgp_per_ri = {}
        # for i in bgp_summary.keys():
        #     print(bgp_summary.keys())
        #     bgp_per_ri.update(bgp_summary_d)
        #     print(bgp_per_ri)
        #     return bgp_per_ri

                # print(bgp_per_ri)
        # print(bgp_per_ri)
        # return bgp_per_ri
                
        
        # json.dump(bgp_summary_d, sp_bgp_f_json, separators=(',', ':'), indent=4, sort_keys=True)
                # bgp_list.append(bgp_summary_d)
            #json.dump(bgp_summary_d, sp_bgp_f_json, separators=(',', ':'), indent=4, sort_keys=True)
            # print(bgp_summary_d)
                # json.dump(bgp_summary_d, sp_bgp_f_json, separators=(',', ':'), indent=4, sort_keys=True)
                # sp_bgp_f_json.write('\n')
        
        # with open('status_page_bgp.txt', 'a') as sp_bgp_f_txt:
        #     for k, v in bgp_summary.items():
        #         for k1, v1 in v['peers'].items():
        #             bgp_summary_list = []
        #             bgp_summary_list.append(str(self.hostname))
        #             bgp_summary_list.append(k)
        #             bgp_summary_list.append(str(k1))
        #             bgp_summary_list.append(str(v1['description']))
        #             bgp_summary_list.append(v1['uptime'])
        #             sp_bgp_f_txt.write(str(bgp_summary_list) + '\n')

    def bgp_dump_json(self):
        pass
        # bgp = []
        # print(self.node_bgp_status)
        # with open('status_page_bgp.json', 'a') as sp_bgp_f_json:
        #    bgp.append(self.node_bgp_status)
        #    json.dump(bgp, sp_bgp_f_json, separators=(',', ':'), indent=4, sort_keys=True)
        """

        bgp_dump = {}
        with open('status_page_bgp.json', 'a') as sp_bgp_f_json:
            for i in self.node_bgp_status:
                bgp_dump.update(i)
                json.dump(bgp_dump, sp_bgp_f_json, separators=(',', ':'), indent=4, sort_keys=True)
        """


    @staticmethod
    def all_bgp_nodes():

        """
        this should work with 'all' as function argument passed over to node_select()
        however, it gets values from the 2nd main dict only. This is a workaround to get all of them
        """

        router_list = []
        for i in NetNode.node_select('DC1', 'router', dcs_db):
            router_list.append(i)
        for j in NetNode.node_select('DC2', 'router', dcs_db):
            router_list.append(j)
        return router_list

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


class NetStatus:

    # def __init__(self):
    #     self = {}

    def get_status(self):
        overall_bgp = []
        for i in NetNode.all_bgp_nodes():
            n = NetNode(i)
            n.node_driver()
            n.node_open()
            n.node_rpc_timeout()
            neigh_per_vrouter = n.node_bgp_status()
            for b in neigh_per_vrouter:
                overall_bgp.append(b)
            n.node_arp_table()
            n.node_close()
        with open('status_page_bgp.json', 'w') as sp_bgp_f_json:
            json.dump(overall_bgp, sp_bgp_f_json, separators=(',', ':'), indent=4, sort_keys=True)


    def get_status_single(self):
        bgp = []
        n = NetNode('vmx2')
        n.node_driver()
        n.node_open()
        n.node_rpc_timeout()
        b = n.node_bgp_status()
        for i in b:
            bgp.append(i)
        n.node_arp_table()
        n.node_close()
        print(bgp)
        with open('single_status_page_bgp.json', 'w') as single_sp_bgp_f_json:
             json.dump(bgp, single_sp_bgp_f_json, separators=(',', ':'), indent=4, sort_keys=True)

        # s.hostname = self.all_bgp_nodes()
        # for i in s.hostname():
        #     print(i)
        
        # all_routers = self.all_bgp_nodes()
        # for i in all_routers:
        #     self.node_open()
        #     self.node_close()
        # print(a)
        # i = NetNode(a)
        # print(i)

        #     self.node_rpc_timeout()
        #     self.node_open()
        #     d = self.bgp_json.update(self.node_bgp_status())
        #     self.node_arp_table()
        #     self.node_close
        #     with open('status_page_bgp.json', 'a') as sp_bgp_f_json:
        #         json.dump(d, sp_bgp_f_json, separators=(',', ':'), indent=4, sort_keys=True)

        """
        clear output files before feeding them with new data
        def node_bgp_status() opens file in append mode
        """

        # with open('status_page_bgp.txt', 'w') as sp_bgp_f_txt:
        #     pass
        # with open('status_page_bgp.json', 'w') as sp_bgp_f_json:
        #     pass
        # bgp_json = {}
        # for i in NetNode.all_bgp_nodes():
        #     self = NetNode(i)
        #     self.node_driver()
        #     self.node_rpc_timeout()
        #     self.node_open()
        #     d = self.node_bgp_status()
        #     self.node_arp_table()
        #     self.node_close()
        #     bgp_json.update(d)

    # def please(self):
    #     print(self.ini
            # with open('status_page_bgp.json', 'a') as sp_bgp_f_json:
            #     json.dump(bpg_json, sp_bgp_f_json, separators=(',', ':'), indent=4, sort_keys=True)

if __name__ == "__main__":
    i = NetStatus()
    i.get_status()

sys.exit()
