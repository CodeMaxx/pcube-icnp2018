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
# 1. Number of probe/update packets generated
########################################################

from scapy.all import rdpcap

from utils import *

def num_probe_packets():
    total_probe_packets = 0

    for i in range(1, NUM_SWITCHES + 1):
        num = 0
        for j in SWITCH_PORTS:
            outgoing_packets = rdpcap("pcap/s%d-eth%d_in.pcap" % (i, j))
            probe_packets = filter(lambda packet: packet[0]['LoadBalancePkt'].preamble == 1 and packet[0]['LoadBalancePkt'].fin == 1, [(LoadBalancePkt(bytes(p)), p.time) for p in outgoing_packets])
            num += len(list(probe_packets))
        print("Probe packets sent by switch %d: %d" % (i, num))
        total_probe_packets += num

    print("Total Probe Packets: %d" % total_probe_packets)

def main():
    cprint("Probe Packets")
    num_probe_packets()

if __name__ == '__main__':
    main()