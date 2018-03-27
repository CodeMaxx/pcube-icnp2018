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

from scapy.all import Packet
from scapy.all import IntField, LongField
import os

NUM_SWITCHES = 4
NUM_PORTS = 6
PCAP_BASE_DIRECTORY = "pcap/"
SWITCH_PORTS = [4,5,6]
SERVER_PORTS = [2,3]
USER_PORTS = [1]

# Print helper function
def cprint(str):
    print("\n" + "-"*25 + " " + str + " " + "-"*25 + "\n")

# Find the index of nth occurance of a substring
def nfind(string, substr, num):
    return string.replace(substr, "\xff"*len(substr), num).find(substr)

def check_empty_file(filepath):
    return os.stat(filepath).st_size == 0

class LoadBalancePkt(Packet):
    name = "LoadBalancePkt"
    fields_desc = [
        LongField("preamble", 0),
        IntField("syn", 0),
        IntField("fin", 0),
        IntField("fid",0),
        IntField("subfid", 0),
        IntField("packet_id", 0),
        IntField("hash",0),
        IntField("count",0),
        IntField("swid", 0),
        IntField("flow_num", 0)
    ]
