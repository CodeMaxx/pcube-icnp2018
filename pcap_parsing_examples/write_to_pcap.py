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
# 1. How to write packets to a pcap file
########################################################

from scapy.all import rdpcap, wrpcap

# Read all the packets from a pcap file in the form of a list
packets = rdpcap('s1-eth1_out.pcap')

# Go over all packets
for packet in packets:
    # Checking for presence of UDP layer
    if packet.haslayer('UDP'):
        # Write only UDP packets to udp.pcap
        wrpcap('udp.pcap', packet, append=True)
