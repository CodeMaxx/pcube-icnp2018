/* Copyright 2018-present IIT Bombay (Akash Trehan, Huzefa Chasmai, Aniket Shirke)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// ------------------ Constants --------------------

#define SERVERS 2

// -------------------- Headers ------------------------

// Stores the preamble (type of packet) and whether it is syn/fin type
// Also stores the flow ID 
header_type load_balancer_t {
    fields {
        preamble: 64;
        syn: 32;
        fin: 32;
        fid: 32;
        subfid : 32;
        packet_id : 32;
        hash : 32;
        _count : 32;
    }
}
header load_balancer_t load_balancer_head;

// Stores switch ID and flow number
header_type switch_info_t {
	fields {
        swid: 32;
        flow_num: 32;
    }
}

header switch_info_t switch_info_head;

// Metadata
header_type meta_t {
    fields {
        // Total flows till now
        total_flow_count : 32;
        // Hash of the packet fid
        hash: 32;
        // Port to send this packet to
        routing_port: 32;
    }
}

metadata meta_t meta;

// ---------------------- Hashing ------------------

// Fields to calculate the hash on
field_list flow_list {
    load_balancer_head.fid;
}

// Hash calculation specifying output width and algo for hashing
field_list_calculation flow_register_index {
    input {
        flow_list;
    }
    algorithm : csum16;
    output_width : 16;
}

//-------------------- Parsers ------------------------

parser start {
    // If the preamble == 0, then execute parse_head
    return select(current(0, 64)) {
        0: parse_head;
        //1: interswitch; // To be used in stateful mode
        default: ingress;
    }
}

// Extracting load balancer header
parser parse_head {
    extract(load_balancer_head);
    return ingress;
}

//------------------ Registers -----------------------

// Stores the number of flows a switch has seen till now
register total_flow_count_register {
    width: 32;
    instance_count: 1;
}

// Stores the mapping of which flow went to which port (server)
register flow_to_port_map_register {
    width: 32;
    instance_count: 65536;
}

// --------------------- Tables -------------------------------

// Do all calculations for selecting port
table set_dest_port_table {
    actions {
        set_dest_port;
    }
    size: 1;
}

// Updates flow_to_port_map_register on a SYN packet
table update_map_table {
	actions {
        update_map;
	}
	size: 1;
}

// Clears flow_to_port_map_register on a FIN packet
table clear_map_table {
    actions {
        clear_map;
    }
    size: 1;
}

// Forwards packets
table forwarding_table {
    reads{
        // If meta.routing_port has been set for this packet
        meta.routing_port: valid;
    }
    actions{
        forward;
        _drop;
    }
    size: 1;
}

// ---------------------------- Actions -----------------------

// Sets the destination port of a packet
action set_dest_port() {
    // Read the number of counts from register into metadata
    register_read(meta.total_flow_count, total_flow_count_register, 0);
    // Set the destination port to (flow count % SERVERS)
    // +2 is because server ports start from 2
    modify_field(standard_metadata.egress_spec, (meta.total_flow_count % SERVERS)+2);
    // Increment number of flows
    add_to_field(meta.total_flow_count, 1);
    // Writeback number of flows to register
    register_write(total_flow_count_register, 0, meta.total_flow_count);
}

action update_map() {
    // Read the hash value for the fid
    modify_field_with_hash_based_offset(meta.hash, 0,
                                        flow_register_index, 65536);
    // Store mapping
    register_write(flow_to_port_map_register, meta.hash, standard_metadata.egress_spec);
}

action clear_map() {
    // Get hash for the fid
    modify_field_with_hash_based_offset(meta.hash, 0,
                                        flow_register_index, 65536);
    // Change mapping to 0
    register_write(flow_to_port_map_register, meta.hash, 0);
}

// Read the port from the mapping register and set egress port accordingly
action forward() {
    modify_field_with_hash_based_offset(meta.hash, 0,
                                        flow_register_index, 65536);
    register_read(meta.routing_port, flow_to_port_map_register, meta.hash);
    modify_field(standard_metadata.egress_spec, meta.routing_port);
}

// Drop packet
action _drop() {
	drop();
}

//------------------------ Control Logic -----------------

control ingress {
    // If a new flow has started
    if(load_balancer_head.syn == 1) {
        // Figure out which port to send it to
    	apply(set_dest_port_table);
        // Store the flow id to port mapping
    	apply(update_map_table);
    }

    // Forward packet
    apply(forwarding_table);

    // If it is a fin packet, then remove the flow id to port mapping
    if(load_balancer_head.fin == 1) {
    	apply(clear_map_table);
    }
}

// Nothing to be done in egress
control egress {
}
