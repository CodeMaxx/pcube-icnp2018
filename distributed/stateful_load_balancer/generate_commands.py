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
# 1. generate commands.txt based on threshold
########################################################

import sys


if len(sys.argv) < 3:
    print("Format: %s <TYPE> <SERVER_THRESHOLD>" % sys.argv[0])
    sys.exit()

THRESHOLD = int(sys.argv[2])
S1PORT = 2
S2PORT = 3

template = open('commands_template_%s.txt'%sys.argv[1], 'r')

s = template.read() + "\n"
template.close()

for s1_load in range(THRESHOLD + 1):
    for s2_load in range(THRESHOLD + 1):
        if s1_load == THRESHOLD and s2_load == THRESHOLD:
            break
        minload = min(s1_load, s2_load)
        port = 0
        if minload == s1_load:
            port = S1PORT
        else:
            port = S2PORT
        s += "table_add set_server_dest_port_table set_server_dest_port %d %d => %d %d\n" % (s1_load, s2_load, minload, port)

commands = open('commands.txt', 'w')
commands.write(s)
commands.close()
