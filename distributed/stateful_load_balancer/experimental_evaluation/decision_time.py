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
# 1. Decision making time for SYN packets
########################################################

from scapy.all import rdpcap

from utils import *

def avg_syn_decision_time():
    avg_time = 0
    total_time = 0
    num_syn_packets = 0

    for i in range(1, NUM_SWITCHES + 1):
        host_packets = rdpcap(PCAP_BASE_DIRECTORY + "s%d-eth1_out.pcap" % i)
        all_outgoing_flow_packets = []
        for j in range(2, NUM_PORTS + 1):
            outgoing_packets = rdpcap(PCAP_BASE_DIRECTORY + "s%d-eth%d_in.pcap" % (i, j))
            all_outgoing_flow_packets += filter(lambda packet: packet[0]['Raw'].load.startswith(b"SYN"), [(LoadBalancePkt(bytes(p)), p.time) for p in outgoing_packets])

        for packet in host_packets:
            p = LoadBalancePkt(bytes(packet))
            p_loadbal_layer = p['LoadBalancePkt']

            # If p is not a SYN packet
            if not p['Raw'].load.startswith(b"SYN"):
                continue

            for packet_match in all_outgoing_flow_packets:
                if p_loadbal_layer.fid == packet_match[0]['LoadBalancePkt'].fid:
                    total_time += packet_match[1] - packet.time
                    num_syn_packets += 1
                    break

    avg_time = total_time/num_syn_packets

    print("Total time taken for forwarding all SYN packets: %s milliseconds" % str(total_time*1000))
    print("Number of SYN packets: %s" % num_syn_packets)
    print("Average decision making time: %s milliseconds" % str(avg_time*1000))

def main():
    cprint("Decision Making Time")
    avg_syn_decision_time()

if __name__ == '__main__':
    main()
