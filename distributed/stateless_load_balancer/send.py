#!/usr/bin/python

# Copyright 2013-present Barefoot Networks, Inc.
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

from scapy.all import sniff, sendp
from scapy.all import Packet
from scapy.all import ShortField, IntField, LongField, BitField

import networkx as nx

import sys

import random

HOSTNAME = sys.argv[1]

class LoadBalancePkt(Packet):
    name = "SrcRoute"
    fields_desc = [
        LongField("preamble", 0),
        FlagField("flags", 0, 2, ["syn", "fin"]),
        StrFixedLenField("fid", '', len=4),
        IntField("swid", 0),
        IntField("flow_num", 0)
    ]


def main():
    num_flows = 10
    for flow in range(num_flows):
        fid = HOSTNAME + " 0" + str(flow)
        p = LoadBalancePkt(flags=0b10, fid=fid) / str(fid)
        print p.show()
        # sendp(p, iface = "eth0")

if __name__ == '__main__':
    main()
