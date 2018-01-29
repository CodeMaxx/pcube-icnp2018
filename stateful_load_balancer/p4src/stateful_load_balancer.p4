/*
Copyright 2013-present Barefoot Networks, Inc. 

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

#define SERVERS 4

header_type load_balancer_t {
    fields {
        preamble: 64;
        num_valid: 32;
        packet_size: 32;
    }
}

header load_balancer_t load_balancer_head;

header_type meta_t {
    fields {
        count1: 32;
        count2: 32;
        count3: 32;
        count4: 32;
        final_port: 32;
    }
}

metadata meta_t meta;

parser start {
    return select(current(0, 64)) {
        0: parse_head;
        default: ingress;
    }
}

parser parse_head {
    extract(load_balancer_head);
    return ingress;
}

action _drop() {
    drop();
}

register size_register {
    width: 32;
    instance_count: 4;
}

action get_port() {
    register_read(meta.count1, size_register, 0);
    register_read(meta.count2, size_register, 1);
    register_read(meta.count3, size_register, 2);
    register_read(meta.count4, size_register, 3);
}

table get_port_table {
    actions {
        get_port;
    }
    size: 1;
}

action route4() {
    modify_field(meta.final_port, 5);
    modify_field(standard_metadata.egress_spec, meta.final_port);
    register_read(meta.count1, size_register, 3);
    add_to_field(meta.count1, load_balancer_head.packet_size);
    register_write(size_register, 3, meta.count1);
}

table route_table4 {
    actions {
        route4;
    }
    size: 1;
}

action route1() {
    modify_field(meta.final_port, 2);
    modify_field(standard_metadata.egress_spec, meta.final_port);
    register_read(meta.count1, size_register, 0);
    add_to_field(meta.count1, load_balancer_head.packet_size);
    register_write(size_register, 0, meta.count1);
}

table route_table1 {
    actions {
        route1;
    }
    size: 1;
}

action route2() {
    modify_field(meta.final_port, 3);
    modify_field(standard_metadata.egress_spec, meta.final_port);
    register_read(meta.count1, size_register, 1);
    add_to_field(meta.count1, load_balancer_head.packet_size);
    register_write(size_register, 1, meta.count1);
}

table route_table2 {
    actions {
        route2;
    }
    size: 1;
}

action route3() {
    modify_field(meta.final_port, 4);
    modify_field(standard_metadata.egress_spec, meta.final_port);
    register_read(meta.count1, size_register, 2);
    add_to_field(meta.count1, load_balancer_head.packet_size);
    register_write(size_register, 2, meta.count1);
}

table route_table3 {
    actions {
        route3;
    }
    size: 1;
}

control ingress {
    apply(get_port_table);
    if(meta.count1 <= meta.count2 and meta.count1 <= meta.count3 and meta.count1 <= meta.count4) {
        apply(route_table1);
    }
    else if(meta.count2 <= meta.count1 and meta.count2 <= meta.count3 and meta.count2 <= meta.count4) {
        apply(route_table2);
    }
    else if(meta.count3 <= meta.count1 and meta.count3 <= meta.count2 and meta.count3 <= meta.count4) {
        apply(route_table3);
    }
    else {
        apply(route_table4);
    }
}

control egress {
}
