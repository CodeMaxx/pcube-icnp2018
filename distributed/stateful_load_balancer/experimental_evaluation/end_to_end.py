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
    for i in range(NUM_SWITCHES):
        try:
            outgoing_packets = rdpcap("pcap/s%d-eth1_in.pcap" % i)
        except:
            continue
        for j in range(NUM_SWITCHES):
            for k in SERVER_PORTS:
                pass


def main():
    cprint("End to End Latency")
    end_to_end_latency()


if __name__ == '__main__':
    main()
