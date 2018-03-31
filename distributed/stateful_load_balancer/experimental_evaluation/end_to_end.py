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
# 1. End to End Latency
########################################################

from utils import *

def end_to_end_latency(pcap_data):
    pcaps = pcap_data.pcaps
    avg_time = 0
    total_time = 0
    num_data_packets = 0
    bla = 0
    # Go through all users
    for i in range(1, NUM_SWITCHES+1):
        try:
            outgoing_packets = pcaps[(i, 1, 'out')]
        except:
            continue
        
        # Get all flow packets sent out by the user
        all_outgoing_flow_packets = filter(lambda packet: 
            packet[0]['Raw'].load.startswith(b"Data") or (packet[0]['Raw'].load.startswith(b"SYN") and 
                packet[0].preamble == 0) or (packet[0]['Raw'].load.startswith(b"FIN") and 
                packet[0].preamble == 0),
             [(LoadBalancePkt(bytes(p)), p.time) for p in outgoing_packets])
        
        # Go through all the packets sent out by user
        for pkt in all_outgoing_flow_packets:
            bla += 1
            p = pkt[0]
            # p.show()
            p_loadbal_layer = p['LoadBalancePkt']
            p_raw = str(p['Raw'].load)
            # print(p_flow_pkt_no)        
            
            # Go through all the switch-server links to find where this packet was finally sent
            for j in range(1, NUM_SWITCHES+1):
                for k in SERVER_PORTS:
                    try:
                        incoming_packets = pcaps[(j, k, 'in')]
                    except:
                        continue
                    for packet_match in incoming_packets:
                        pkm = LoadBalancePkt(bytes(packet_match))
                        raw = str(pkm['Raw'].load)
                        # pkm.show()

                        if pkm['LoadBalancePkt'].preamble != 0:
                            continue

                        # For SYN packets
                        if p_loadbal_layer.fid == pkm['LoadBalancePkt'].fid and p_loadbal_layer.subfid == pkm['LoadBalancePkt'].subfid and pkm['LoadBalancePkt'].syn == 1 and p_loadbal_layer.syn == 1:
                            total_time += packet_match.time - pkt[1]
                            num_data_packets += 1
                            break
                        
                        # For FIN packets
                        if p_loadbal_layer.fid == pkm['LoadBalancePkt'].fid and p_loadbal_layer.subfid == pkm['LoadBalancePkt'].subfid and pkm['LoadBalancePkt'].fin == 1 and p_loadbal_layer.fin == 1:
                            total_time += packet_match.time - pkt[1]
                            num_data_packets += 1
                            break
                                
                        # For Data packets
                        if p_loadbal_layer.fid == pkm['LoadBalancePkt'].fid and p_loadbal_layer.subfid == pkm['LoadBalancePkt'].subfid and p_loadbal_layer.packet_id == pkm['LoadBalancePkt'].packet_id:
                            total_time += packet_match.time - pkt[1]
                            num_data_packets += 1
                            break

    avg_time = total_time/num_data_packets

    print("Total time taken for all packets to reach their destination: %s milliseconds" % str(total_time*1000))
    print("Number of packets: %s" % num_data_packets)
    print("Average End to End latency: %s milliseconds" % str(avg_time*1000))
    print(bla)

def main(pcap_data):
    cprint("End to End Latency")
    end_to_end_latency(pcap_data)


if __name__ == '__main__':
    pcap_data = PcapData()
    main(pcap_data)
