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

from scapy.all import sniff, sendp
from scapy.all import Packet
from scapy.all import ShortField, IntField, LongField, BitField

import networkx as nx

import sys

import random

class SrcRoute(Packet):
    name = "SrcRoute"
    fields_desc = [
        LongField("preamble", 0),
        IntField("num_valid", 2),
        IntField("packet_size", 256),
    ]

def read_topo():
    nb_hosts = 0
    nb_switches = 0
    links = []
    with open("topo.txt", "r") as f:
        line = f.readline()[:-1]
        w, nb_switches = line.split()
        assert(w == "switches")
        line = f.readline()[:-1]
        w, nb_hosts = line.split()
        assert(w == "hosts")
        for line in f:
            if not f: break
            a, b = line.split()
            links.append( (a, b) )
    return int(nb_hosts), int(nb_switches), links

def main():

    nb_hosts, nb_switches, links = read_topo()

    n = 100
    C1 = 0; C2 = 0; C3 = 0; C4 = 0
    print C1, C2, C3, C4
    host = 0
    while(n):
        packet_size = random.randint(0, 256)
        # packet_size = 5
        if(C1 <= C2 and C1 <= C3 and C1 <= C4):
            C1 += packet_size
            host = 2
        elif(C2 <= C1 and C2 <= C3 and C2 <= C4):
            host = 3
            C2 += packet_size
        elif(C3 <= C1 and C3 <= C2 and C3 <= C4):
            host = 4
            C3 += packet_size
        else:
            host = 5
            C4 += packet_size
        p = SrcRoute(num_valid = 4, packet_size=packet_size) / (str(packet_size) + " " + str(host))
        print p.show()
        sendp(p, iface = "eth0")
        n-=1

if __name__ == '__main__':
    main()
