#!/usr/bin/python

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

from scapy.all import rdpcap

from utils import *

def link_traffic():
    total_hosts = len(USER_PORTS) + len(SERVER_PORTS)
    eth_no = total_hosts + 1
    for i in range(1, NUM_SWITCHES + 1):
        # Traffic over links with users and servers
        for j in (USER_PORTS + SERVER_PORTS):
            outgoing_packets = rdpcap("pcap/s%d-eth%d_in.pcap" % (i, j))
            incoming_packets = rdpcap("pcap/s%d-eth%d_out.pcap" % (i, j))
            all_packets = outgoing_packets + incoming_packets
            num_pkts = sum([1 for pkt in all_packets])
            total_pkt_size = sum([len(pkt) for pkt in all_packets])

            host_number = (i - 1)*(total_hosts) + j
            print("Number of packets over link s%d-h%d: %d" % (i, host_number, num_pkts))
            print("Data through the link s%d-h%d: %d bytes\n" % (i, host_number, total_pkt_size))


        # Traffic over links with other switches
        eth_copy = eth_no
        for j in range(i+1, NUM_SWITCHES + 1):
            incoming1 = rdpcap("pcap/s%d-eth%d_out.pcap" % (i, eth_copy))
            incoming2 = rdpcap("pcap/s%d-eth%d_out.pcap" % (j, total_hosts + i))
            all_packets = incoming1 + incoming2
            num_pkts = sum([1 for pkt in all_packets])
            total_pkt_size = sum([len(pkt) for pkt in all_packets])

            print("Number of packets over link s%d-s%d: %d" % (i, j, num_pkts))
            print("Data through the link s%d-s%d: %d bytes\n" % (i, j, total_pkt_size))

            eth_copy += 1

        eth_no += 1

def main():
    cprint("Traffic over all links")
    link_traffic()

if __name__ == '__main__':
    main()
