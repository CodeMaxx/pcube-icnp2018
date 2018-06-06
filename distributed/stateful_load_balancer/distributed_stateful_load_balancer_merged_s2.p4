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

#define 80 80
#define 20 20
#define 2 2
#define 12 12
#define 11 11
#define 1 1
#define 99 99
#define 10000 10000

// -------------------- Headers ------------------------

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

header_type sync_info_t {
    fields {
        flow_num: 32;
    }
}
header sync_info_t sync_info_head;

header_type meta_t {
    fields {
        temp : 32;

            server_flow1 : 32;

            switch_flow1 : 32;
            switch_flow2 : 32;
            switch_flow3 : 32;
            switch_flow4 : 32;
            switch_flow5 : 32;
            switch_flow6 : 32;
            switch_flow7 : 32;
            switch_flow8 : 32;
            switch_flow9 : 32;
            switch_flow10 : 32;
            switch_flow11 : 32;

        hash: 16;
        routing_port: 32;

        min_flow_len : 32;

        probe_bool : 32;
    }
}
metadata meta_t meta;

header_type intrinsic_metadata_t {
    fields {
        mcast_grp : 16;
        egress_rid : 16;
    }
}
metadata intrinsic_metadata_t intrinsic_metadata;

// ---------------------- Hashing ------------------

field_list flow_list {
    load_balancer_head.fid;
}

field_list_calculation flow_register_index {
    input {
        flow_list;
    }
    algorithm : crc16;
    output_width : 16;
}

//-------------------- Parsers ------------------------

parser start {
    return select(current(0, 64)) {
        0: parse_head;
        1: interswitch;
        default: ingress;
    }
}

parser parse_head {
    extract(load_balancer_head);
    extract(sync_info_head);
    return ingress;
}

parser interswitch {
    extract(load_balancer_head);
    extract(sync_info_head);
    return ingress;
}

//------------------ Registers -----------------------

register total_flow_count_register {
    width: 32;
    instance_count: 2 + 12;
}

register flow_to_port_map_register {
    width: 32;
    instance_count: 65536;
}

// --------------------- Tables -------------------------------

table get_server_flow_count_table{
    actions{
        get_server_flow_count;
    }
    size:1;
}

    table update_min_flow_len1_table1 {
        actions{
            update_min_flow_len1;
        }
        size: 1;
    }

table send_update_table {
    actions{
        send_update;
    }
    size: 1;
}

table update_switch_flow_count_table {
    actions{
        update_switch_flow_count;
    }
    size: 1;
}

table set_server_dest_port_table{
    reads{
            meta.server_flow1 : exact;
    }
    actions{
        set_server_dest_port;
    }
    size:10000;
}

table set_probe_bool_table {
    actions{
        set_probe_bool;
    }
    size: 1;
}

table get_switch_flow_count_table{
    actions{
        get_switch_flow_count;
    }
    size:1;
}

    table set_switch1_dest_port_table{
        actions{
            set_switch1_dest_port;
        }
        size:1;
    }
    table set_switch2_dest_port_table{
        actions{
            set_switch2_dest_port;
        }
        size:1;
    }
    table set_switch3_dest_port_table{
        actions{
            set_switch3_dest_port;
        }
        size:1;
    }
    table set_switch4_dest_port_table{
        actions{
            set_switch4_dest_port;
        }
        size:1;
    }
    table set_switch5_dest_port_table{
        actions{
            set_switch5_dest_port;
        }
        size:1;
    }
    table set_switch6_dest_port_table{
        actions{
            set_switch6_dest_port;
        }
        size:1;
    }
    table set_switch7_dest_port_table{
        actions{
            set_switch7_dest_port;
        }
        size:1;
    }
    table set_switch8_dest_port_table{
        actions{
            set_switch8_dest_port;
        }
        size:1;
    }
    table set_switch9_dest_port_table{
        actions{
            set_switch9_dest_port;
        }
        size:1;
    }
    table set_switch10_dest_port_table{
        actions{
            set_switch10_dest_port;
        }
        size:1;
    }
    table set_switch11_dest_port_table{
        actions{
            set_switch11_dest_port;
        }
        size:1;
    }

table update_map_table {
    actions {
        update_map;
    }
    size: 1;
}

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

table drop_table {
    actions {
        _drop;
    }
    size: 1;
}

table send_probe_table {
    actions{
        send_probe;
    }
    size: 1;
}

table clear_map_table {
    actions {
        clear_map;
    }
    size: 1;
}

table update_flow_count_table {
    actions{
        update_flow_count;
    }
    size: 1;
}

    table update_min_flow_len1_table2 {
        actions{
            update_min_flow_len1;
        }
        size: 1;
    }

table send_broadcast_update_table {
    actions{
        send_broadcast_update;
    }
    size: 1;
}

// ---------------------------- Actions -----------------------

action get_server_flow_count(){

        register_read(meta.server_flow1,total_flow_count_register,1 - 1);
}

    action update_min_flow_len1(){
        modify_field(meta.min_flow_len, meta.server_flow1);
    }

//--->Will be generated as _mirror_1() in a separate file
action send_update(){
    modify_field(load_balancer_head.preamble,2);
modify_field(sync_info_head.flow_num,(meta.server_flow1);
    modify_field(standard_metadata.egress_spec, standard_metadata.ingress_port);
}

action update_switch_flow_count() {
    register_write(total_flow_count_register,standard_metadata.ingress_port - 2, sync_info_head.flow_num);
}

action set_server_dest_port(flow_count,flow_dest){
    register_write(total_flow_count_register,flow_dest - 2, flow_count + 1);
    modify_field(standard_metadata.egress_spec,flow_dest);
}

action set_probe_bool(){
    modify_field(meta.probe_bool,1);
}

action get_switch_flow_count(){
        register_read(meta.switch_flow1,total_flow_count_register,1 + 12 - 1);
        register_read(meta.switch_flow2,total_flow_count_register,2 + 12 - 1);
        register_read(meta.switch_flow3,total_flow_count_register,3 + 12 - 1);
        register_read(meta.switch_flow4,total_flow_count_register,4 + 12 - 1);
        register_read(meta.switch_flow5,total_flow_count_register,5 + 12 - 1);
        register_read(meta.switch_flow6,total_flow_count_register,6 + 12 - 1);
        register_read(meta.switch_flow7,total_flow_count_register,7 + 12 - 1);
        register_read(meta.switch_flow8,total_flow_count_register,8 + 12 - 1);
        register_read(meta.switch_flow9,total_flow_count_register,9 + 12 - 1);
        register_read(meta.switch_flow10,total_flow_count_register,10 + 12 - 1);
        register_read(meta.switch_flow11,total_flow_count_register,11 + 12 - 1);
}

    action set_switch1_dest_port(){
        register_write(total_flow_count_register,1 + 12 - 1, meta.switch_flow1 + 1);
        modify_field(standard_metadata.egress_spec,1 + 12 + 1);
    }
    action set_switch2_dest_port(){
        register_write(total_flow_count_register,2 + 12 - 1, meta.switch_flow2 + 1);
        modify_field(standard_metadata.egress_spec,2 + 12 + 1);
    }
    action set_switch3_dest_port(){
        register_write(total_flow_count_register,3 + 12 - 1, meta.switch_flow3 + 1);
        modify_field(standard_metadata.egress_spec,3 + 12 + 1);
    }
    action set_switch4_dest_port(){
        register_write(total_flow_count_register,4 + 12 - 1, meta.switch_flow4 + 1);
        modify_field(standard_metadata.egress_spec,4 + 12 + 1);
    }
    action set_switch5_dest_port(){
        register_write(total_flow_count_register,5 + 12 - 1, meta.switch_flow5 + 1);
        modify_field(standard_metadata.egress_spec,5 + 12 + 1);
    }
    action set_switch6_dest_port(){
        register_write(total_flow_count_register,6 + 12 - 1, meta.switch_flow6 + 1);
        modify_field(standard_metadata.egress_spec,6 + 12 + 1);
    }
    action set_switch7_dest_port(){
        register_write(total_flow_count_register,7 + 12 - 1, meta.switch_flow7 + 1);
        modify_field(standard_metadata.egress_spec,7 + 12 + 1);
    }
    action set_switch8_dest_port(){
        register_write(total_flow_count_register,8 + 12 - 1, meta.switch_flow8 + 1);
        modify_field(standard_metadata.egress_spec,8 + 12 + 1);
    }
    action set_switch9_dest_port(){
        register_write(total_flow_count_register,9 + 12 - 1, meta.switch_flow9 + 1);
        modify_field(standard_metadata.egress_spec,9 + 12 + 1);
    }
    action set_switch10_dest_port(){
        register_write(total_flow_count_register,10 + 12 - 1, meta.switch_flow10 + 1);
        modify_field(standard_metadata.egress_spec,10 + 12 + 1);
    }
    action set_switch11_dest_port(){
        register_write(total_flow_count_register,11 + 12 - 1, meta.switch_flow11 + 1);
        modify_field(standard_metadata.egress_spec,11 + 12 + 1);
    }

action update_map() {
    modify_field_with_hash_based_offset(meta.hash, 0,
                                        flow_register_index, 65536);
    register_write(flow_to_port_map_register, meta.hash, standard_metadata.egress_spec);
}

action forward() {
    modify_field_with_hash_based_offset(meta.hash, 0,
                                        flow_register_index, 65536);
    register_read(meta.routing_port, flow_to_port_map_register, meta.hash);
    modify_field(standard_metadata.egress_spec, meta.routing_port);
    modify_field(load_balancer_head.hash,meta.hash);
}

field_list meta_list {
    meta;
    standard_metadata;
    intrinsic_metadata;
}

//--->Will be generated as _sync_1() in a separate file
action send_probe(){
    clone_ingress_pkt_to_egress(standard_metadata.egress_spec,meta_list);
    modify_field(load_balancer_head.preamble, 1);
    modify_field(intrinsic_metadata.mcast_grp, 1);
}

action clear_map() {
    modify_field_with_hash_based_offset(meta.hash, 0,
                                        flow_register_index, 65536);
    register_write(flow_to_port_map_register, meta.hash, 0);
}

action update_flow_count() {
    register_read(meta.temp, total_flow_count_register, meta.routing_port-2);
    add_to_field(meta.temp,-1);
    register_write(total_flow_count_register,meta.routing_port-2, meta.temp);
}

//--->Will be generated as _sync_2() in a separate file
action send_broadcast_update(){
    clone_ingress_pkt_to_egress(standard_metadata.egress_spec,meta_list);
    modify_field(load_balancer_head.preamble,2);
modify_field(sync_info_head.flow_num,(meta.server_flow1);
    modify_field(intrinsic_metadata.mcast_grp, 1);
}

action _drop() {
    drop();
}

//------------------------ Control Logic -----------------

control ingress {
    apply(get_server_flow_count_table); 

    //Preamble 1 => Probe packet 
    if (load_balancer_head.preamble == 1){

        //Send update (set preamble as 2)
        @mirror(true,
                2,
(meta.server_flow1)
        //--->apply(send_update_table);
    }
    //Preamble 2 => Update packet
    else if (load_balancer_head.preamble == 2){
        //update the registers
        apply(update_switch_flow_count_table);
    }
    //Default Preamble is 0
    else {

        //-------------------------------------------------------------------------
        //Start of flow
        if(load_balancer_head.syn == 1) {

            //Forwarding to own server
            if(@bool[1,2,1](<) [meta.server_flow1, 99]){
                //Forwarding can be done locally
                apply(set_server_dest_port_table);

                //Take decision to send probe packet or not (Reactive)
if ((meta.server_flow1)*100 > (80 * 2 * 99)){
                    apply(set_probe_bool_table);
                }
            }
            //Forwarding to another switch
            else{
                //Choose from switches
                apply(get_switch_flow_count_table);

                if (@bool[1,12,1](>=) [meta.switch_flow$i, 2*99] ){
                    apply(drop_table);
                }
                else {
                        if(meta.switch_flow1 <= meta.switch_flow2 and meta.switch_flow1 <= meta.switch_flow3 and meta.switch_flow1 <= meta.switch_flow4 and meta.switch_flow1 <= meta.switch_flow5 and meta.switch_flow1 <= meta.switch_flow6 and meta.switch_flow1 <= meta.switch_flow7 and meta.switch_flow1 <= meta.switch_flow8 and meta.switch_flow1 <= meta.switch_flow9 and meta.switch_flow1 <= meta.switch_flow10 and meta.switch_flow1 <= meta.switch_flow11) {
                            apply(set_switch1_dest_port_table);
                        }
                        else if(meta.switch_flow2 <= meta.switch_flow1 and meta.switch_flow2 <= meta.switch_flow3 and meta.switch_flow2 <= meta.switch_flow4 and meta.switch_flow2 <= meta.switch_flow5 and meta.switch_flow2 <= meta.switch_flow6 and meta.switch_flow2 <= meta.switch_flow7 and meta.switch_flow2 <= meta.switch_flow8 and meta.switch_flow2 <= meta.switch_flow9 and meta.switch_flow2 <= meta.switch_flow10 and meta.switch_flow2 <= meta.switch_flow11) {
                            apply(set_switch2_dest_port_table);
                        }
                        else if(meta.switch_flow3 <= meta.switch_flow1 and meta.switch_flow3 <= meta.switch_flow2 and meta.switch_flow3 <= meta.switch_flow4 and meta.switch_flow3 <= meta.switch_flow5 and meta.switch_flow3 <= meta.switch_flow6 and meta.switch_flow3 <= meta.switch_flow7 and meta.switch_flow3 <= meta.switch_flow8 and meta.switch_flow3 <= meta.switch_flow9 and meta.switch_flow3 <= meta.switch_flow10 and meta.switch_flow3 <= meta.switch_flow11) {
                            apply(set_switch3_dest_port_table);
                        }
                        else if(meta.switch_flow4 <= meta.switch_flow1 and meta.switch_flow4 <= meta.switch_flow2 and meta.switch_flow4 <= meta.switch_flow3 and meta.switch_flow4 <= meta.switch_flow5 and meta.switch_flow4 <= meta.switch_flow6 and meta.switch_flow4 <= meta.switch_flow7 and meta.switch_flow4 <= meta.switch_flow8 and meta.switch_flow4 <= meta.switch_flow9 and meta.switch_flow4 <= meta.switch_flow10 and meta.switch_flow4 <= meta.switch_flow11) {
                            apply(set_switch4_dest_port_table);
                        }
                        else if(meta.switch_flow5 <= meta.switch_flow1 and meta.switch_flow5 <= meta.switch_flow2 and meta.switch_flow5 <= meta.switch_flow3 and meta.switch_flow5 <= meta.switch_flow4 and meta.switch_flow5 <= meta.switch_flow6 and meta.switch_flow5 <= meta.switch_flow7 and meta.switch_flow5 <= meta.switch_flow8 and meta.switch_flow5 <= meta.switch_flow9 and meta.switch_flow5 <= meta.switch_flow10 and meta.switch_flow5 <= meta.switch_flow11) {
                            apply(set_switch5_dest_port_table);
                        }
                        else if(meta.switch_flow6 <= meta.switch_flow1 and meta.switch_flow6 <= meta.switch_flow2 and meta.switch_flow6 <= meta.switch_flow3 and meta.switch_flow6 <= meta.switch_flow4 and meta.switch_flow6 <= meta.switch_flow5 and meta.switch_flow6 <= meta.switch_flow7 and meta.switch_flow6 <= meta.switch_flow8 and meta.switch_flow6 <= meta.switch_flow9 and meta.switch_flow6 <= meta.switch_flow10 and meta.switch_flow6 <= meta.switch_flow11) {
                            apply(set_switch6_dest_port_table);
                        }
                        else if(meta.switch_flow7 <= meta.switch_flow1 and meta.switch_flow7 <= meta.switch_flow2 and meta.switch_flow7 <= meta.switch_flow3 and meta.switch_flow7 <= meta.switch_flow4 and meta.switch_flow7 <= meta.switch_flow5 and meta.switch_flow7 <= meta.switch_flow6 and meta.switch_flow7 <= meta.switch_flow8 and meta.switch_flow7 <= meta.switch_flow9 and meta.switch_flow7 <= meta.switch_flow10 and meta.switch_flow7 <= meta.switch_flow11) {
                            apply(set_switch7_dest_port_table);
                        }
                        else if(meta.switch_flow8 <= meta.switch_flow1 and meta.switch_flow8 <= meta.switch_flow2 and meta.switch_flow8 <= meta.switch_flow3 and meta.switch_flow8 <= meta.switch_flow4 and meta.switch_flow8 <= meta.switch_flow5 and meta.switch_flow8 <= meta.switch_flow6 and meta.switch_flow8 <= meta.switch_flow7 and meta.switch_flow8 <= meta.switch_flow9 and meta.switch_flow8 <= meta.switch_flow10 and meta.switch_flow8 <= meta.switch_flow11) {
                            apply(set_switch8_dest_port_table);
                        }
                        else if(meta.switch_flow9 <= meta.switch_flow1 and meta.switch_flow9 <= meta.switch_flow2 and meta.switch_flow9 <= meta.switch_flow3 and meta.switch_flow9 <= meta.switch_flow4 and meta.switch_flow9 <= meta.switch_flow5 and meta.switch_flow9 <= meta.switch_flow6 and meta.switch_flow9 <= meta.switch_flow7 and meta.switch_flow9 <= meta.switch_flow8 and meta.switch_flow9 <= meta.switch_flow10 and meta.switch_flow9 <= meta.switch_flow11) {
                            apply(set_switch9_dest_port_table);
                        }
                        else if(meta.switch_flow10 <= meta.switch_flow1 and meta.switch_flow10 <= meta.switch_flow2 and meta.switch_flow10 <= meta.switch_flow3 and meta.switch_flow10 <= meta.switch_flow4 and meta.switch_flow10 <= meta.switch_flow5 and meta.switch_flow10 <= meta.switch_flow6 and meta.switch_flow10 <= meta.switch_flow7 and meta.switch_flow10 <= meta.switch_flow8 and meta.switch_flow10 <= meta.switch_flow9 and meta.switch_flow10 <= meta.switch_flow11) {
                            apply(set_switch10_dest_port_table);
                        }
                        else if(meta.switch_flow11 <= meta.switch_flow1 and meta.switch_flow11 <= meta.switch_flow2 and meta.switch_flow11 <= meta.switch_flow3 and meta.switch_flow11 <= meta.switch_flow4 and meta.switch_flow11 <= meta.switch_flow5 and meta.switch_flow11 <= meta.switch_flow6 and meta.switch_flow11 <= meta.switch_flow7 and meta.switch_flow11 <= meta.switch_flow8 and meta.switch_flow11 <= meta.switch_flow9 and meta.switch_flow11 <= meta.switch_flow10) {
                            apply(set_switch11_dest_port_table);
                        }
                }
                
            }

            //Remember mapping for the flow
            apply(update_map_table);
        }
        //-------------------------------------------------------------------------

        //Forwarding
        apply(forwarding_table);

        if (meta.routing_port == 0){
            apply(drop_table);
        }

        @sync(  meta.probe_bool == 1,
                1,
                1)
        /*--->if(meta.probe_bool == 1){
            apply(send_probe_table);
        }*/

        //-------------------------------------------------------------------------
        //End of flow
        if(load_balancer_head.fin == 1) {

            //Clear mappings
            apply(clear_map_table);
            apply(update_flow_count_table);

            //Take decision to send probe packet or not (Proactive)
            @sync(
( meta.server_flow1)*100 < (20 * 2 * 99) and (meta.routing_port == 2 or meta.routing_port == 3),
                    2,
                    1,
(meta.server_flow1))
            
/*--->if ((meta.server_flow1 + meta.server_flow2)*100 < (20 * 2 * 99)){
                if(meta.routing_port == 2 or meta.routing_port == 3){
                    
                    //Send broadcast (set preamble as 2)
                    apply(send_broadcast_update_table);
                }
            }*/
        }
        //-------------------------------------------------------------------------
    }
}

control egress {
}
