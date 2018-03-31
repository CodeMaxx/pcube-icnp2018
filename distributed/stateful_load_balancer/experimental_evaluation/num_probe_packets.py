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
# 1. Number of probe/update packets generated
########################################################

from utils import *

def num_probe_packets(pcap_data):
    pcaps = pcap_data.pcaps
    total_reactive = 0
    total_proactive = 0

    # Go through all switches
    for i in range(1, NUM_SWITCHES + 1):
        num_r = 0
        num_p = 0
        # Go through all swtich ports for that switch
        for j in SWITCH_PORTS:
            try:
                # packets going out from a switch to other switches
                outgoing_packets = pcaps[(i, j, "in")]
            except:
                continue
            # Filter out all the probe packets
            proactive_probe_packets = filter(lambda packet: (packet[0]['LoadBalancePkt'].preamble == 2 or packet[0]['LoadBalancePkt'].preamble == 1)
             and packet[0]['LoadBalancePkt'].fin == 1 , [(LoadBalancePkt(bytes(p)), p.time) for p in outgoing_packets])
            reactive_probe_packets = filter(lambda packet: (packet[0]['LoadBalancePkt'].preamble == 2 or packet[0]['LoadBalancePkt'].preamble == 1)
             and packet[0]['LoadBalancePkt'].syn == 1 , [(LoadBalancePkt(bytes(p)), p.time) for p in outgoing_packets])
            
            # Accumulate number of probe packets sent out by each switch
            num_r += len(list(reactive_probe_packets))
            num_p += len(list(proactive_probe_packets))
        print("Reactive, Proactive packets sent by switch %d: %d, %d" % (i, num_r, num_p))
        total_reactive += num_r
        total_proactive += num_p

    print("Total Reactive Packets: %d" % total_reactive)
    print("Total Proactive Packets: %d" % total_proactive)

def main(pcap_data):
    cprint("Probe Packets")
    num_probe_packets(pcap_data)

if __name__ == '__main__':
    pcap_data = PcapData()
    main(pcap_data)
