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

from scapy.all import rdpcap

from utils import *

def end_to_end_latency():
    avg_time = 0
    total_time = 0
    num_data_packets = 0
    bla = 0
    # Go through all users
    for i in range(1, NUM_SWITCHES+1):
        try:
            outgoing_packets = rdpcap("pcap/s%d-eth1_out.pcap" % i)
        except:
            continue
        
        # Get all flow packets sent out by the user
        all_outgoing_flow_packets = filter(lambda packet: 
            packet[0]['Raw'].load.startswith(b"Data") or packet[0]['Raw'].load.startswith(b"SYN") or packet[0]['Raw'].load.startswith(b"FIN"),
             [(LoadBalancePkt(bytes(p)), p.time) for p in outgoing_packets])
        
        # Go through all the packets sent out by user
        for pkt in all_outgoing_flow_packets:
            bla += 1
            p = pkt[0]
            # p.show()
            p_loadbal_layer = p['LoadBalancePkt']
            p_raw = str(p['Raw'].load)
            # Extract the packet number for this fid
            p_flow_pkt_no = p_raw[nfind(p_raw,'-',2) + 1: nfind(p_raw,'-',3)]
            # print(p_flow_pkt_no)        
            
            # Go through all the switch-server links to find where this packet was finally sent
            for j in range(1, NUM_SWITCHES+1):
                for k in SERVER_PORTS:
                    try:
                        incoming_packets = rdpcap("pcap/s%d-eth%d_in.pcap" % (j, k))
                    except:
                        continue
                    for packet_match in incoming_packets:
                        pkm = LoadBalancePkt(bytes(packet_match))
                        raw = str(pkm['Raw'].load)
                        flow_pkt_num = raw[nfind(raw,'-',2) + 1: nfind(raw,'-',3)]
                        # pkm.show()

                        # For SYN packets
                        if p_loadbal_layer.fid == pkm['LoadBalancePkt'].fid and pkm['LoadBalancePkt'].syn == 1 and p['LoadBalancePkt'].syn == 1:
                            total_time += packet_match.time - pkt[1]
                            num_data_packets += 1
                            break
                        
                        # For FIN packets
                        if p_loadbal_layer.fid == pkm['LoadBalancePkt'].fid and pkm['LoadBalancePkt'].fin == 1 and p['LoadBalancePkt'].fin == 1:
                            total_time += packet_match.time - pkt[1]
                            num_data_packets += 1
                            break
                                
                        # For Data packets
                        if p_loadbal_layer.fid == pkm['LoadBalancePkt'].fid and flow_pkt_num.isdigit() and flow_pkt_num == p_flow_pkt_no:
                            total_time += packet_match.time - pkt[1]
                            num_data_packets += 1
                            break

    avg_time = total_time/num_data_packets

    print("Total time taken for all packets to reach their destination: %s milliseconds" % str(total_time*1000))
    print("Number of packets: %s" % num_data_packets)
    print("Average End to End latency: %s milliseconds" % str(avg_time*1000))
    print(bla)

def main():
    cprint("End to End Latency")
    end_to_end_latency()


if __name__ == '__main__':
    main()
