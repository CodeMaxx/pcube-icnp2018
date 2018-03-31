#!/usr/bin/env python2
import argparse
import os
from time import sleep

import p4runtime_lib.bmv2
import p4runtime_lib.helper

SWITCH_TO_HOST_PORT = 1
SWITCH_TO_SWITCH_PORT = 2

def writeTunnelRules(p4info_helper, ingress_sw, egress_sw, tunnel_id,
                     dst_eth_addr, dst_ip_addr):
    '''
    Installs three rules:
    1) An tunnel ingress rule on the ingress switch in the ipv4_lpm table that
       encapsulates traffic into a tunnel with the specified ID
    2) A transit rule on the ingress switch that forwards traffic based on
       the specified ID
    3) An tunnel egress rule on the egress switch that decapsulates traffic
       with the specified ID and sends it to the host

    :param p4info_helper: the P4Info helper
    :param ingress_sw: the ingress switch connection
    :param egress_sw: the egress switch connection
    :param tunnel_id: the specified tunnel ID
    :param dst_eth_addr: the destination IP to match in the ingress rule
    :param dst_ip_addr: the destination Ethernet address to write in the
                        egress rule
    '''
    # 1) Tunnel Ingress Rule
    table_entry = p4info_helper.buildTableEntry(
        table_name="ipv4_lpm",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
        },
        action_name="myTunnel_ingress",
        action_params={
            "dst_id": tunnel_id,
        })
    ingress_sw.WriteTableEntry(table_entry)
    print "Installed ingress tunnel rule on %s" % ingress_sw.name

    # 2) Tunnel Transit Rule
    # The rule will need to be added to the myTunnel_exact table and match on
    # the tunnel ID (hdr.myTunnel.dst_id). Traffic will need to be forwarded
    # using the myTunnel_forward action on the port connected to the next switch.
    #
    # For our simple topology, switch 1 and switch 2 are connected using a
    # link attached to port 2 on both switches. We have defined a variable at
    # the top of the file, SWITCH_TO_SWITCH_PORT, that you can use as the output
    # port for this action.
    #
    # We will only need a transit rule on the ingress switch because we are
    # using a simple topology. In general, you'll need on transit rule for
    # each switch in the path (except the last switch, which has the egress rule),
    # and you will need to select the port dynamically for each switch based on
    # your topology.

    # TODO build the transit rule
    table_entry = p4info_helper.buildTableEntry(
        table_name="myTunnel_exact",
        match_fields={
            "hdr.myTunnel.dst_id" : (tunnel_id),
        },
        action_name="myTunnel_forward",
        action_params={
            "port" : SWITCH_TO_SWITCH_PORT,
        })
    ingress_sw.WriteTableEntry(table_entry)
    # TODO install the transit rule on the ingress switch
    print "Installed transit tunnel rule on %s" % ingress_sw.name

    # 3) Tunnel Egress Rule
    # For our simple topology, the host will always be located on the
    # SWITCH_TO_HOST_PORT (port 1).
    # In general, you will need to keep track of which port the host is
    # connected to.
    table_entry = p4info_helper.buildTableEntry(
        table_name="myTunnel_exact",
        match_fields={
            "hdr.myTunnel.dst_id": tunnel_id
        },
        action_name="myTunnel_egress",
        action_params={
            "dstAddr": dst_eth_addr,
            "port": SWITCH_TO_HOST_PORT
        })
    egress_sw.WriteTableEntry(table_entry)
    print "Installed egress tunnel rule on %s" % egress_sw.name

def writeSourceRules(p4info_helper1,source_sw,dst_ip_addr,dst_ether_addr,egress_port):
    # sets ipv4 table rules
    print "p4info_helper1 in writeSourceRules = ", p4info_helper1
    table_entry = p4info_helper1.buildTableEntry(
        table_name="ipv4_lpm",
        match_fields={
            "hdr.ipv4.dstAddr" : (dst_ip_addr, 32)
        },
        action_name="ipv4_forward",
        action_params={
        "dmac" : dst_ether_addr,
        "out_port" : egress_port
        })
    source_sw.WriteTableEntry(table_entry)
    print "Installes ipv4 forward rule on %s" % source_sw.name

def initializeSourceRules(p4info_helper1,source_sw,instruction_count,mask1,mask2):
    #add table entry for tb_int_source
    print "p4info_helper1 = ", p4info_helper1
    table_entry = p4info_helper1.buildTableEntry(
        table_name="tb_int_source",
        match_fields={

        },
        action_name="process_int_source_headers.int_source_dscp",
        action_params={
        "ins_cnt": instruction_count,
        "ins_mask0003": mask1,
        "ins_mask0407": mask2
        })
    source_sw.WriteTableEntry(table_entry)
    print "Installed int source rule on %s" % source_sw.name

def int_prepRules(p4_infohelper,source_sw,switch_id):
    table_entry = p4_infohelper.buildTableEntry(
        table_name="int_prep",
        match_fields={},
        action_name="Int_transit_egress.int_transit",
        action_params={
            "switch_id" : switch_id
        })
    source_sw.WriteTableEntry(table_entry)
    print "Installed int_prep table rule on %s" % source_sw.name

def table_int_inst_0003(p4info_helper,source_sw,mask1,action_to_take):
    table_entry = p4info_helper.buildTableEntry(
        table_name="Int_transit_egress.int_metadata_insert.int_inst_0003",
        match_fields={
        "hdr.int_header.instruction_mask_0003" : mask1
        },
        action_name=action_to_take,
        action_params={

        })
    source_sw.WriteTableEntry(table_entry)
    print "Installed int_inst_0003 table rule on %s" % source_sw.name

def table_int_inst_0407(p4info_helper,source_sw,mask2,action_to_take):
    table_entry = p4info_helper.buildTableEntry(
        table_name="Int_transit_egress.int_metadata_insert.int_inst_0407",
        match_fields={
        "hdr.int_header.instruction_mask_0407" : mask2
        },
        action_name=action_to_take,
        action_params={

        })
    source_sw.WriteTableEntry(table_entry)
    print "Installed int_inst_0407 table rule on %s" % source_sw.name


def writeTransitRules(p4info_helper2,source_sw,dst_ip_addr,dst_ether_addr,egress_port):
    table_entry = p4info_helper2.buildTableEntry(
        table_name="ipv4_lpm",
        match_fields={
            "hdr.ipv4.dstAddr" : (dst_ip_addr, 32)
        },
        action_name="ipv4_forward",
        action_params={
        "dmac" : dst_ether_addr,
        "out_port" : egress_port
        })
    source_sw.WriteTableEntry(table_entry)
    print "Installes ipv4 forward rule on %s" % source_sw.name

def writeSinkRules(p4info_helper3,source_sw,dst_ip_addr,dst_ether_addr,egress_port):
    table_entry = p4info_helper3.buildTableEntry(
        table_name="ipv4_lpm",
        match_fields={
            "hdr.ipv4.dstAddr" : (dst_ip_addr, 32)
        },
        action_name="ipv4_forward",
        action_params={
        "dmac" : dst_ether_addr,
        "out_port" : egress_port
        })
    source_sw.WriteTableEntry(table_entry)
    print "Installes ipv4 forward rule on %s" % source_sw.name

def tb_generate_reportSink(p4info_helper3,source_sw,instance_type,mon_dst_mac):
    table_entry=p4info_helper3.buildTableEntry(
        table_name="process_int_clone.tb_generate_report",
        match_fields={
            "standard_metadata.instance_type": instance_type
        },
        action_name="process_int_clone.set_mon_params",
        action_params={
            "mon_dmac": mon_dst_mac
        })
    source_sw.WriteTableEntry(table_entry)
    print "Installes tb_generate_report rule on %s" % source_sw.name


def readTableRules(p4info_helper, sw):
    '''
    Reads the table entries from all tables on the switch.

    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    '''
    print '\n----- Reading tables rules for %s -----' % sw.name
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            # TODO For extra credit, you can use the p4info_helper to translate
            #      the IDs the entry to names
            print entry
            print '-----'

def printCounter(p4info_helper, sw, counter_name, index):
    '''
    Reads the specified counter at the specified index from the switch. In our
    program, the index is the tunnel ID. If the index is 0, it will return all
    values from the counter.

    :param p4info_helper: the P4Info helper
    :param sw:  the switch connection
    :param counter_name: the name of the counter from the P4 program
    :param index: the counter index (in our case, the tunnel ID)
    '''
    for response in sw.ReadCounters(p4info_helper.get_counters_id(counter_name), index):
        for entity in response.entities:
            counter = entity.counter_entry
            print "%s %s %d: %d packets (%d bytes)" % (
                sw.name, counter_name, index,
                counter.data.packet_count, counter.data.byte_count
            )


def main(p4info_file_path1, bmv2_file_path1,p4info_file_path2, bmv2_file_path2,p4info_file_path3, bmv2_file_path3):
    # Instantiate a P4 Runtime helper from the p4info file
    p4info_helper1 = p4runtime_lib.helper.P4InfoHelper(p4info_file_path1)
    p4info_helper2 = p4runtime_lib.helper.P4InfoHelper(p4info_file_path2)
    p4info_helper3 = p4runtime_lib.helper.P4InfoHelper(p4info_file_path3)
    # Create a switch connection object for s1 and s2;
    # this is backed by a P4 Runtime gRPC connection
    s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection('s1', address='127.0.0.1:50051')
    s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection('s2', address='127.0.0.1:50052')
    s3 = p4runtime_lib.bmv2.Bmv2SwitchConnection('s3', address='127.0.0.1:50053')
    s4 = p4runtime_lib.bmv2.Bmv2SwitchConnection('s4', address='127.0.0.1:50054')
    s5 = p4runtime_lib.bmv2.Bmv2SwitchConnection('s5', address='127.0.0.1:50055')
    s6 = p4runtime_lib.bmv2.Bmv2SwitchConnection('s6', address='127.0.0.1:50056')
    s7 = p4runtime_lib.bmv2.Bmv2SwitchConnection('s7', address='127.0.0.1:50057')
    s8 = p4runtime_lib.bmv2.Bmv2SwitchConnection('s8', address='127.0.0.1:50058')

    # Install the P4 program on the switches
    s1.SetForwardingPipelineConfig(p4info=p4info_helper1.p4info,
                                   bmv2_json_file_path=bmv2_file_path1)
    print "Installed P4 Program using SetForwardingPipelineConfig on %s" % s1.name
    s2.SetForwardingPipelineConfig(p4info=p4info_helper2.p4info,
                                   bmv2_json_file_path=bmv2_file_path2)
    print "Installed P4 Program using SetForwardingPipelineConfig on %s" % s2.name
    s3.SetForwardingPipelineConfig(p4info=p4info_helper2.p4info,
                                   bmv2_json_file_path=bmv2_file_path2)
    print "Installed P4 Program using SetForwardingPipelineConfig on %s" % s3.name
    s4.SetForwardingPipelineConfig(p4info=p4info_helper2.p4info,
                                   bmv2_json_file_path=bmv2_file_path2)
    print "Installed P4 Program using SetForwardingPipelineConfig on %s" % s4.name
    s5.SetForwardingPipelineConfig(p4info=p4info_helper2.p4info,
                                   bmv2_json_file_path=bmv2_file_path2)
    print "Installed P4 Program using SetForwardingPipelineConfig on %s" % s5.name
    s6.SetForwardingPipelineConfig(p4info=p4info_helper2.p4info,
                                   bmv2_json_file_path=bmv2_file_path2)
    print "Installed P4 Program using SetForwardingPipelineConfig on %s" % s6.name
    s7.SetForwardingPipelineConfig(p4info=p4info_helper2.p4info,
                                   bmv2_json_file_path=bmv2_file_path2)
    print "Installed P4 Program using SetForwardingPipelineConfig on %s" % s7.name
    s8.SetForwardingPipelineConfig(p4info=p4info_helper3.p4info,
                                   bmv2_json_file_path=bmv2_file_path3)
    print "Installed P4 Program using SetForwardingPipelineConfig on %s" % s8.name

    #Write INT_source switch rules
    #writeSourceRules(p4info_helper1,source_sw=s1,dst_ip_addr="10.0.1.1",dst_ether_addr="00:00:00:00:01:01",egress_port=1)
    writeSourceRules(p4info_helper1,source_sw=s1,dst_ip_addr="10.0.8.2",dst_ether_addr="00:00:00:00:08:02",egress_port=2)
    writeSourceRules(p4info_helper1,source_sw=s1,dst_ip_addr="10.0.8.3",dst_ether_addr="00:00:00:00:08:03",egress_port=2)
    initializeSourceRules(p4info_helper1,source_sw=s1,instruction_count=3,mask1=11,mask2=0)
    int_prepRules(p4info_helper1,source_sw=s1,switch_id=1)
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=0,action_to_take="int_set_header_0003_i0")
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=1,action_to_take="int_set_header_0003_i1")
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=2,action_to_take="int_set_header_0003_i2")
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=3,action_to_take="int_set_header_0003_i3")
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=4,action_to_take="int_set_header_0003_i4")
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=5,action_to_take="int_set_header_0003_i5")
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=6,action_to_take="int_set_header_0003_i6")
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=7,action_to_take="int_set_header_0003_i7")
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=8,action_to_take="int_set_header_0003_i8")
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=10,action_to_take="int_set_header_0003_i10")
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=9,action_to_take="int_set_header_0003_i9")
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=12,action_to_take="int_set_header_0003_i12")
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=11,action_to_take="int_set_header_0003_i11")
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=14,action_to_take="int_set_header_0003_i14")
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=13,action_to_take="int_set_header_0003_i13")
    table_int_inst_0003(p4info_helper1,source_sw=s1,mask1=15,action_to_take="int_set_header_0003_i15")

    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=0,action_to_take="int_set_header_0407_i0")
    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=1,action_to_take="int_set_header_0407_i1")
    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=3,action_to_take="int_set_header_0407_i3")
    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=2,action_to_take="int_set_header_0407_i2")
    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=4,action_to_take="int_set_header_0407_i4")
    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=5,action_to_take="int_set_header_0407_i5")
    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=6,action_to_take="int_set_header_0407_i6")
    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=8,action_to_take="int_set_header_0407_i8")
    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=7,action_to_take="int_set_header_0407_i7")
    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=9,action_to_take="int_set_header_0407_i9")
    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=10,action_to_take="int_set_header_0407_i10")
    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=11,action_to_take="int_set_header_0407_i11")
    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=12,action_to_take="int_set_header_0407_i12")
    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=13,action_to_take="int_set_header_0407_i13")
    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=14,action_to_take="int_set_header_0407_i14")
    table_int_inst_0407(p4info_helper1,source_sw=s1,mask2=15,action_to_take="int_set_header_0407_i15")

    #Write INT_transit switch rules
    writeSourceRules(p4info_helper2,source_sw=s2,dst_ip_addr="10.0.8.3",dst_ether_addr="00:00:00:00:08:03",egress_port=2)
    writeSourceRules(p4info_helper2,source_sw=s2,dst_ip_addr="10.0.8.2",dst_ether_addr="00:00:00:00:08:02",egress_port=2)
    int_prepRules(p4info_helper2,source_sw=s2,switch_id=2)
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=0,action_to_take="int_set_header_0003_i0")
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=1,action_to_take="int_set_header_0003_i1")
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=2,action_to_take="int_set_header_0003_i2")
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=3,action_to_take="int_set_header_0003_i3")
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=4,action_to_take="int_set_header_0003_i4")
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=5,action_to_take="int_set_header_0003_i5")
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=6,action_to_take="int_set_header_0003_i6")
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=7,action_to_take="int_set_header_0003_i7")
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=8,action_to_take="int_set_header_0003_i8")
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=10,action_to_take="int_set_header_0003_i10")
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=9,action_to_take="int_set_header_0003_i9")
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=12,action_to_take="int_set_header_0003_i12")
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=11,action_to_take="int_set_header_0003_i11")
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=14,action_to_take="int_set_header_0003_i14")
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=13,action_to_take="int_set_header_0003_i13")
    table_int_inst_0003(p4info_helper1,source_sw=s2,mask1=15,action_to_take="int_set_header_0003_i15")

    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=0,action_to_take="int_set_header_0407_i0")
    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=1,action_to_take="int_set_header_0407_i1")
    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=3,action_to_take="int_set_header_0407_i3")
    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=2,action_to_take="int_set_header_0407_i2")
    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=4,action_to_take="int_set_header_0407_i4")
    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=5,action_to_take="int_set_header_0407_i5")
    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=6,action_to_take="int_set_header_0407_i6")
    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=8,action_to_take="int_set_header_0407_i8")
    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=7,action_to_take="int_set_header_0407_i7")
    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=9,action_to_take="int_set_header_0407_i9")
    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=10,action_to_take="int_set_header_0407_i10")
    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=11,action_to_take="int_set_header_0407_i11")
    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=12,action_to_take="int_set_header_0407_i12")
    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=13,action_to_take="int_set_header_0407_i13")
    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=14,action_to_take="int_set_header_0407_i14")
    table_int_inst_0407(p4info_helper1,source_sw=s2,mask2=15,action_to_take="int_set_header_0407_i15")

    writeSourceRules(p4info_helper2,source_sw=s3,dst_ip_addr="10.0.8.2",dst_ether_addr="00:00:00:00:08:02",egress_port=2)
    writeSourceRules(p4info_helper2,source_sw=s3,dst_ip_addr="10.0.8.3",dst_ether_addr="00:00:00:00:08:03",egress_port=2)
    int_prepRules(p4info_helper2,source_sw=s3,switch_id=3)
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=0,action_to_take="int_set_header_0003_i0")
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=1,action_to_take="int_set_header_0003_i1")
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=2,action_to_take="int_set_header_0003_i2")
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=3,action_to_take="int_set_header_0003_i3")
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=4,action_to_take="int_set_header_0003_i4")
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=5,action_to_take="int_set_header_0003_i5")
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=6,action_to_take="int_set_header_0003_i6")
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=7,action_to_take="int_set_header_0003_i7")
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=8,action_to_take="int_set_header_0003_i8")
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=10,action_to_take="int_set_header_0003_i10")
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=9,action_to_take="int_set_header_0003_i9")
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=12,action_to_take="int_set_header_0003_i12")
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=11,action_to_take="int_set_header_0003_i11")
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=14,action_to_take="int_set_header_0003_i14")
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=13,action_to_take="int_set_header_0003_i13")
    table_int_inst_0003(p4info_helper1,source_sw=s3,mask1=15,action_to_take="int_set_header_0003_i15")

    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=0,action_to_take="int_set_header_0407_i0")
    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=1,action_to_take="int_set_header_0407_i1")
    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=3,action_to_take="int_set_header_0407_i3")
    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=2,action_to_take="int_set_header_0407_i2")
    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=4,action_to_take="int_set_header_0407_i4")
    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=5,action_to_take="int_set_header_0407_i5")
    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=6,action_to_take="int_set_header_0407_i6")
    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=8,action_to_take="int_set_header_0407_i8")
    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=7,action_to_take="int_set_header_0407_i7")
    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=9,action_to_take="int_set_header_0407_i9")
    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=10,action_to_take="int_set_header_0407_i10")
    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=11,action_to_take="int_set_header_0407_i11")
    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=12,action_to_take="int_set_header_0407_i12")
    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=13,action_to_take="int_set_header_0407_i13")
    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=14,action_to_take="int_set_header_0407_i14")
    table_int_inst_0407(p4info_helper1,source_sw=s3,mask2=15,action_to_take="int_set_header_0407_i15")

    writeSourceRules(p4info_helper2,source_sw=s7,dst_ip_addr="10.0.8.2",dst_ether_addr="00:00:00:00:08:02",egress_port=5)
    writeSourceRules(p4info_helper2,source_sw=s7,dst_ip_addr="10.0.8.3",dst_ether_addr="00:00:00:00:08:03",egress_port=5)
    int_prepRules(p4info_helper2,source_sw=s7,switch_id=7)
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=0,action_to_take="int_set_header_0003_i0")
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=1,action_to_take="int_set_header_0003_i1")
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=2,action_to_take="int_set_header_0003_i2")
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=3,action_to_take="int_set_header_0003_i3")
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=4,action_to_take="int_set_header_0003_i4")
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=5,action_to_take="int_set_header_0003_i5")
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=6,action_to_take="int_set_header_0003_i6")
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=7,action_to_take="int_set_header_0003_i7")
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=8,action_to_take="int_set_header_0003_i8")
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=10,action_to_take="int_set_header_0003_i10")
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=9,action_to_take="int_set_header_0003_i9")
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=12,action_to_take="int_set_header_0003_i12")
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=11,action_to_take="int_set_header_0003_i11")
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=14,action_to_take="int_set_header_0003_i14")
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=13,action_to_take="int_set_header_0003_i13")
    table_int_inst_0003(p4info_helper1,source_sw=s7,mask1=15,action_to_take="int_set_header_0003_i15")

    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=0,action_to_take="int_set_header_0407_i0")
    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=1,action_to_take="int_set_header_0407_i1")
    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=3,action_to_take="int_set_header_0407_i3")
    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=2,action_to_take="int_set_header_0407_i2")
    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=4,action_to_take="int_set_header_0407_i4")
    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=5,action_to_take="int_set_header_0407_i5")
    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=6,action_to_take="int_set_header_0407_i6")
    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=8,action_to_take="int_set_header_0407_i8")
    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=7,action_to_take="int_set_header_0407_i7")
    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=9,action_to_take="int_set_header_0407_i9")
    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=10,action_to_take="int_set_header_0407_i10")
    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=11,action_to_take="int_set_header_0407_i11")
    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=12,action_to_take="int_set_header_0407_i12")
    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=13,action_to_take="int_set_header_0407_i13")
    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=14,action_to_take="int_set_header_0407_i14")
    table_int_inst_0407(p4info_helper1,source_sw=s7,mask2=15,action_to_take="int_set_header_0407_i15")


    #Write INT_sink switch rules
    writeSourceRules(p4info_helper3,source_sw=s8,dst_ip_addr="10.0.8.2",dst_ether_addr="00:00:00:00:08:02",egress_port=1)
    writeSourceRules(p4info_helper3,source_sw=s8,dst_ip_addr="10.0.8.3",dst_ether_addr="00:00:00:00:08:03",egress_port=2)
    tb_generate_reportSink(p4info_helper3,source_sw=s8,instance_type=1,mon_dst_mac="00:00:00:00:08:03")



    '''
    # Write the rules that tunnel traffic from h1 to h2
    writeTunnelRules(p4info_helper, ingress_sw=s1, egress_sw=s2, tunnel_id=100,
                     dst_eth_addr="00:00:00:00:02:02", dst_ip_addr="10.0.2.2")

    # Write the rules that tunnel traffic from h2 to h1
    writeTunnelRules(p4info_helper, ingress_sw=s2, egress_sw=s1, tunnel_id=200,
                     dst_eth_addr="00:00:00:00:01:01", dst_ip_addr="10.0.1.1")
    '''

    # TODO Uncomment the following two lines to read table entries from s1 and s2
    readTableRules(p4info_helper1, s1)
    readTableRules(p4info_helper2, s2)
    readTableRules(p4info_helper2, s3)
    readTableRules(p4info_helper2, s4)
    readTableRules(p4info_helper2, s5)
    readTableRules(p4info_helper2, s6)
    readTableRules(p4info_helper2, s7)
    readTableRules(p4info_helper3, s8)

    # Print the tunnel counters every 2 seconds
    '''
    try:
        while True:
            sleep(2)
            print '\n----- Reading tunnel counters -----'
            printCounter(p4info_helper, s1, "ingressTunnelCounter", 100)
            printCounter(p4info_helper, s2, "egressTunnelCounter", 100)
            printCounter(p4info_helper, s2, "ingressTunnelCounter", 200)
            printCounter(p4info_helper, s1, "egressTunnelCounter", 200)
    except KeyboardInterrupt:
        print " Shutting down."
    '''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info1', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/int_source.p4info')
    parser.add_argument('--bmv2-json1', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/int_source.json')
    parser.add_argument('--p4info2', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/int_transit.p4info')
    parser.add_argument('--bmv2-json2', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/int_transit.json')
    parser.add_argument('--p4info3', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/int_sink.p4info')
    parser.add_argument('--bmv2-json3', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/int_sink.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info1):
        parser.print_help()
        print "\np4info file not found: %s\nHave you run 'make'?" % args.p4info
        parser.exit(1)
    if not os.path.exists(args.bmv2_json1):
        parser.print_help()
        print "\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json
        parser.exit(1)

    main(args.p4info1, args.bmv2_json1,args.p4info2, args.bmv2_json2,args.p4info3, args.bmv2_json3)
