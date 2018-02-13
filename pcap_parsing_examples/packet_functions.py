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
# 1. How to print packet
# 2. Create copy of packet
# 3. Add layers to the packet
# 4. Edit fields of packet
# 5. Get fields as a dictionary
# 6. Other Miscellaneous commands
########################################################

from scapy.all import rdpcap

# Read all the packets from a pcap file in the form of a list
packets = rdpcap('s1-eth1_out.pcap')

# Print helper function
def cprint(str):
    print("\n" + "-"*25 + " " + str + " " + "-"*25 + "\n")

######################################################################################################
# List of all possible functions. We'll go over a few of these.
#
# ['__bool__', '__bytes__', '__class__', '__contains__', '__delattr__', '__delitem__', '__dict__',
# '__dir__', '__div__', '__doc__', '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__',
# '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__',
# '__lt__', '__module__', '__mul__', '__ne__', '__new__', '__rdiv__', '__reduce__', '__reduce_ex__',
# '__repr__', '__rmul__', '__rtruediv__', '__setattr__', '__setitem__', '__sizeof__', '__str__',
# '__subclasshook__', '__truediv__', '__weakref__', '_do_summary', 'add_payload', 'add_underlayer',
# 'aliastypes', 'answers', 'build', 'build_done', 'build_padding', 'build_ps', 'canvas_dump',
# 'clone_with', 'command', 'copy', 'decode_payload_as', 'default_fields', 'default_payload_class',
# 'delfieldval', 'dispatch_hook', 'display', 'dissect', 'dissection_done', 'do_build', 'do_build_payload',
# 'do_build_ps', 'do_dissect', 'do_dissect_payload', 'do_init_fields', 'explicit', 'extract_padding',
# 'fields', 'fields_desc', 'fieldtype', 'firstlayer', 'fragment', 'from_hexcap', 'get_field', 'getbyteval',
# 'getdictval', 'getfield_and_val', 'getfieldval', 'getlayer', 'getstrval', 'guess_payload_class',
# 'hashret', 'haslayer', 'hide_defaults', 'init_fields', 'initialized', 'lastlayer', 'libnet', 'lower_bonds',
# 'mysummary', 'name', 'original', 'overload_fields', 'overloaded_fields', 'packetfields', 'payload',
# 'payload_guess', 'pdfdump', 'post_build', 'post_dissect', 'post_dissection', 'post_transforms',
# 'pre_dissect', 'psdump', 'raw_packet_cache', 'remove_payload', 'remove_underlayer', 'route',
# 'self_build', 'sent_time', 'setfieldval', 'show', 'show2', 'show_indent', 'sprintf', 'summary',
# 'time', 'underlayer', 'upper_bonds', 'wirelen']
#########################################################################################################

######## Printing initial packet
cprint("Initial packet")
packets[0].show()

######## Create a copy of the packet object
cprint("Copy of packet")
p1 = packets[0].copy()
p1.show()

######## Add a payload to the packet. This acts as the 'Raw' layer which is at the top of the packet.
cprint("Packet with added payload")
p1.add_payload(b"IITB P4: Added using add_payload() function")
p1.show()

######## Editting fields in a packet
cprint("Editted Packet")
# Note: We used p1['Ethernet'] to get just the Ethernet layer.
# Another way to get a layer is p1.getlayer('IPv6')
# Method 1
p1['Ethernet'].setfieldval('type',0xc0ffee)
# Method 2
p1.getlayer('IPv6').version = 100
p1.show()

######## Get Scapy command to generate this packet
cprint("Scapy command to generate above packet")
print(p1.command())

######## Get all fields of a particular layer as a dictionary
cprint("All fields of IPv6 layer")
print(p1['IPv6'].fields)

######## Print a one line summary of packet
cprint("Packet Summary")
print(p1.summary())
