#!/usr/bin/env python3

# Copyright 2018-present Akash Trehan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

########################################################
# 1. Time taken to forward data packets
########################################################

from utils import *
from scapy.all import PacketList

def link_traffic(pcap_data):
    pcaps = pcap_data.pcaps
    total_hosts = len(USER_PORTS) + len(SERVER_PORTS)
    eth_no = total_hosts + 1
    for i in range(1, NUM_SWITCHES + 1):
        # Traffic over links with users and servers
        for j in (USER_PORTS + SERVER_PORTS):
            all_packets = PacketList()
            try:
                # Packets outgoing to host or server
                outgoing_packets = pcaps[(i, j, "in")]
                all_packets += outgoing_packets
            except:
                pass
                
            try:
                # Packets incoming from host or server
                incoming_packets = pcaps[(i, j, "out")]
                all_packets += incoming_packets
            except:
                if not all_packets:
                    continue
                else:
                    pass
            # Number of packets
            num_pkts = sum([1 for pkt in all_packets])
            # Total size of all packets
            total_pkt_size = sum([len(pkt) for pkt in all_packets])

            host_number = (i - 1)*(total_hosts) + j
            print("Number of packets over link s%d-h%d: %d" % (i, host_number, num_pkts))
            print("Data through the link s%d-h%d: %d bytes\n" % (i, host_number, total_pkt_size))


        # Traffic over links with other switches
        eth_copy = eth_no
        for j in range(i+1, NUM_SWITCHES + 1):
            all_packets = PacketList()
            try:
                # Packets exchanged between a pair of switches
                incoming1 = pcaps[(i, eth_copy, "out")]
                all_packets += incoming1
            except:
                pass
            try:
                incoming2 = pcaps[(j, total_hosts + i, "out")]
                all_packets += incoming2
            except:
                if not all_packets:
                    continue
                else:
                    pass
                
            all_packets = incoming1 + incoming2
            # Number of packets
            num_pkts = sum([1 for pkt in all_packets])
            # Total size of all packets
            total_pkt_size = sum([len(pkt) for pkt in all_packets])

            print("Number of packets over link s%d-s%d: %d" % (i, j, num_pkts))
            print("Data through the link s%d-s%d: %d bytes\n" % (i, j, total_pkt_size))

            eth_copy += 1

        eth_no += 1

def main(pcap_data):
    cprint("Traffic over all links")
    link_traffic(pcap_data)

if __name__ == '__main__':
    pcap_data = PcapData()
    main(pcap_data)
