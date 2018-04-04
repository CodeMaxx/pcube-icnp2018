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

def avg_data_forwarding_time(pcap_data):
    pcaps = pcap_data.pcaps
    avg_time = 0
    total_time = 0
    num_data_packets = 0
    bla = 0
    # Go through all users
    for i in range(1, NUM_SWITCHES + 1):
        try:
            host_packets = pcaps[(i, 1, "out")]
        except:
            continue
        outgoing_dict = {}
        # Go through all non-users on the switch and get packets going from switch to them
        for j in range(2, NUM_PORTS + 1):
            try:
                outgoing_packets = pcaps[(i, j, "in")]
            except:
                continue
            # Also store the timestamp of the packets
            # all_outgoing_flow_packets += filter(lambda packet: packet[0]['Raw'].load.startswith(b"Data"), \
            #     [(LoadBalancePkt(bytes(p)), p.time) for p in outgoing_packets])
            # Filter out all the data packets and convert them to LoadBalancerPkt
            for p in outgoing_packets:
                packet = LoadBalancePkt(bytes(p))
                if packet['Raw'].load.startswith(b"Data"):
                    loadbal_layer = packet['LoadBalancePkt']
                    outgoing_dict[(loadbal_layer.fid, loadbal_layer.subfid, loadbal_layer.packet_id)] = \
                        (packet, p.time)
        # For all the user packets
        for packet in host_packets:
            p = LoadBalancePkt(bytes(packet))
            p_loadbal_layer = p['LoadBalancePkt']
            # Extract the packet number for this fid

            # If p is not a Data packet
            if not p['Raw'].load.startswith(b"Data"):
                continue
            bla +=1

            try:
                packet_match = outgoing_dict[(
                    p_loadbal_layer.fid, p_loadbal_layer.subfid, p_loadbal_layer.packet_id)]
                total_time += packet_match[1] - packet.time
                num_data_packets += 1
            except:
                p.show()
    avg_time = total_time/num_data_packets

    print("Total time taken for forwarding all Data packets: %s milliseconds" % str(total_time*1000))
    print("Number of Data packets: %s" % num_data_packets)
    print("Average forwarding time: %s milliseconds" % str(avg_time*1000))
    print(bla)

def main(pcap_data):
    cprint("Data Forwarding Time")
    avg_data_forwarding_time(pcap_data)

if __name__ == '__main__':
    pcap_data = PcapData()
    main(pcap_data)
