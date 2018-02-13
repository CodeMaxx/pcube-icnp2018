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
# 1. How to read packets for custom protocols
########################################################

from scapy.all import rdpcap
from scapy.all import Packet
from scapy.all import IntField, LongField

# Print helper function
def cprint(str):
    print("\n" + "-"*25 + " " + str + " " + "-"*25 + "\n")

# Defining a custom protocol layer
class LoadBalancePkt(Packet):
    name = "LoadBalancePkt"
    fields_desc = [
        LongField("preamble", 0),
        IntField("syn", 0),
        IntField("fin", 0),
        IntField("fid",0),
        IntField("hash",0),
        IntField("count",0),
        IntField("swid", 0),
        IntField("flow_num", 0)
    ]

# Read all the packets from a pcap file in the form of a list
packets = rdpcap('s1-eth1_out.pcap')

# I know beforehand that the packet `packets[32]` is a packet adhering to our protocol
p1 = packets[32].copy()

# Getting the packet as raw bytes
p1_bytes = bytes(p1)

# Convert the bytes into a custom protocol packet. Now all the packet functions are applicable on this
p2 = LoadBalancePkt(p1_bytes)

cprint("Custom protocol packet read from pcap")
p2.show()
