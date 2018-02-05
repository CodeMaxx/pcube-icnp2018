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
#define SYN 1
#define FIN 2

// -------------------- Headers ------------------------

header_type load_balancer_t {
    fields {
        preamble: 64;
        flags: 2;
        fid: 32;
    }
}
header load_balancer_t load_balancer_head;

header_type switch_info_t {
	fields {
        swid: 32;
        flow_num: 32;
    }
}

header switch_info_t switch_info_head;

header_type meta_t {
    fields {
        total_flow_count : 32;
        hash: 32;
        routing_port: 32;
    }
}

metadata meta_t meta;

// ---------------------- Hashing ------------------

field_list flow_list {
    load_balancer_t.fid;
}

field_list_calculation flow_register_index {
    input {
        flow_list;
    }
    algorithm : csum16;
    output_width : 16;
}

//-------------------- Parsers ------------------------

parser start {
    return select(current(0, 64)) {
        0: parse_head;
        //1: interswitch; // To be used in stateful mode
        default: ingress;
    }
}

parser parse_head {
    extract(load_balancer_head);
    return ingress;
}

//---------------- Drop -------------------------------

action _drop() {
    drop();
}

//------------------ Registers -----------------------

register total_flow_count_register {
    width: 32;
    instance_count: 1;
}

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
        meta.routing_port: valid;
    }
    actions{
        forward;
        _drop;
    }
    size: 1;
}

// ---------------------------- Actions -----------------------

action set_dest_port() {
    register_read(meta.total_flow_count, total_flow_count_register, 0);
    modify_field(standard_metadata.egress_spec, (meta.total_flow_count % SERVERS)+2);
    add_to_field(meta.total_flow_count, 1);
    register_write(total_flow_count_register, 0, meta.total_flow_count);
}

action update_map() {
    modify_field_with_hash_based_offset(meta.hash, 0,
                                        flow_register_index, 16);
    register_write(flow_to_port_map_register, meta.hash, standard_metadata.egress_spec);
}

action clear_map() {
    modify_field_with_hash_based_offset(meta.hash, 0,
                                        flow_register_index, 16);
    register_write(flow_to_port_map_register, meta.hash, 0);
}

action forward() {
    modify_field_with_hash_based_offset(meta.hash, 0,
                                        flow_register_index, 16);
    register_read(meta.routing_port, flow_to_port_map_register, meta.hash);
    modify_field(standard_metadata.egress_spec, meta.routing_port);
}

action _drop() {
	drop();
}

//------------------------ Control Logic -----------------

control ingress {
    if(load_balancer_head.flags == SYN) {
    	apply(set_dest_port_table);
    	apply(update_map_table);
    }

    apply(forwarding_table);

    if(load_balancer_head.flags == FIN) {
    	apply(clear_map_table);
    }
}

control egress {
}
