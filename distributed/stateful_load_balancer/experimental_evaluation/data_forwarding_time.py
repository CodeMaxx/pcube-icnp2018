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

def avg_data_forwarding_time():
    avg_time = 0
    total_time = 0
    num_data_packets = 0

    for i in range(1, NUM_SWITCHES + 1):
        host_packets = rdpcap("pcap/s%d-eth1_out.pcap" % i)
        all_outgoing_flow_packets = []
        for j in range(2, NUM_PORTS + 1):
            outgoing_packets = rdpcap("pcap/s%d-eth%d_in.pcap" % (i, j))
            all_outgoing_flow_packets += filter(lambda packet: packet[0]['Raw'].load.startswith(b"Data"), [(LoadBalancePkt(bytes(p)), p.time) for p in outgoing_packets])

        for packet in host_packets:
            p = LoadBalancePkt(bytes(packet))
            p_loadbal_layer = p['LoadBalancePkt']
            p_raw = str(p['Raw'].load)
            p_flow_pkt_no = p_raw[nfind(p_raw,'-',2) + 1: nfind(p_raw,'-',3)]

            # If p is not a Data packet
            if not p['Raw'].load.startswith(b"Data"):
                continue

            for packet_match in all_outgoing_flow_packets:
                raw = str(packet_match[0]['Raw'].load)
                # print("Debug", packet_match[0]['Raw'])
                flow_pkt_num = raw[nfind(raw,'-',2) + 1: nfind(raw,'-',3)]
                if p_loadbal_layer.fid == packet_match[0]['LoadBalancePkt'].fid and flow_pkt_num.isdigit() and flow_pkt_num == p_flow_pkt_no:
                    # DEBUG if code
                    if(packet_match[1] - packet.time) < 0:
                        print(flow_pkt_num)
                        continue
                    total_time += packet_match[1] - packet.time
                    num_data_packets += 1
                    break

    avg_time = total_time/num_data_packets

    print("Total time taken for forwarding all Data packets: %s milliseconds" % str(total_time*1000))
    print("Number of Data packets: %s" % num_data_packets)
    print("Average forwarding time: %s milliseconds" % str(avg_time*1000))

def main():
    cprint("Data Forwarding Time")
    avg_data_forwarding_time()

if __name__ == '__main__':
    main()
