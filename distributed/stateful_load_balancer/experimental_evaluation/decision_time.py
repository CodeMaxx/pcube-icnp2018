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

from utils import *

def avg_syn_decision_time(pcap_data):
    pcaps = pcap_data.pcaps
    avg_time = 0
    total_time = 0
    num_syn_packets = 0
    bla = 0
    # Go through all users
    for i in range(1, NUM_SWITCHES + 1):
        try:
            host_packets = pcaps[(i, 1, "out")]
        except:
            continue
        all_outgoing_flow_packets = []
        outgoing_dict = {}
        # Go through all non-users on the switch and get packets going from switch to them
        for j in range(2, NUM_PORTS + 1):
            try:
                outgoing_packets = pcaps[(i, j, "in")]
            except:
                continue
            # Filter out all the SYN packets and convert them to LoadBalancerPkt
            # Also store the timestamp of the packets
            # all_outgoing_flow_packets += filter(lambda packet: packet[0]['Raw'].load.startswith(b"SYN") and 
            #     packet[0].preamble == 0, [(LoadBalancePkt(bytes(p)), p.time) for p in outgoing_packets])
            for p in outgoing_packets:
                packet = LoadBalancePkt(bytes(p))
                if packet['Raw'].load.startswith(b"SYN") and packet.preamble == 0:
                    loadbal_layer = packet['LoadBalancePkt']
                    outgoing_dict[(loadbal_layer.fid, loadbal_layer.subfid)] = (packet, p.time)
        # For all the user packets
        for packet in host_packets:
            p = LoadBalancePkt(bytes(packet))
            p_loadbal_layer = p['LoadBalancePkt']
            # If p is not a SYN packet
            if not (p['Raw'].load.startswith(b"SYN") and p['LoadBalancePkt'].preamble == 0):
                continue

            bla += 1
            # Find packet matching the host packet
            try:
                packet_match=outgoing_dict[(p_loadbal_layer.fid, p_loadbal_layer.subfid)]
                total_time += packet_match[1] - packet.time
                num_syn_packets += 1
            except:
                p.show()

    avg_time = total_time/num_syn_packets

    print("Total time taken for forwarding all SYN packets: %s milliseconds" % str(total_time*1000))
    print("Number of SYN packets: %s" % num_syn_packets)
    print("Average decision making time: %s milliseconds" % str(avg_time*1000))
    print(bla)

def main(pcap_data):
    cprint("Decision Making Time")
    avg_syn_decision_time(pcap_data)

if __name__ == '__main__':
    pcap_data = PcapData()
    main(pcap_data)
