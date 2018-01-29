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
    }
}

header load_balancer_t load_balancer_head;

header_type meta_t {
    fields {
        register_tmp : 32;
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

register round_robin_register {
    width: 32;
    static: route_pkt;
    instance_count: 4;
}

//Ports start from 1,2,3...
action route() {
    register_read(meta.register_tmp, round_robin_register, 0);
    modify_field(standard_metadata.egress_spec, meta.register_tmp % SERVERS);
    add_to_field(standard_metadata.egress_spec, 2);
    add_to_field(meta.register_tmp, 1);
    register_write(round_robin_register,0,meta.register_tmp);
}

table route_pkt {
    reads {
        load_balancer_head.num_valid: valid;
    }
    actions {
        route;
        _drop;
    }
    size: 1;
}

control ingress {
    apply(route_pkt);
}

control egress {
}
