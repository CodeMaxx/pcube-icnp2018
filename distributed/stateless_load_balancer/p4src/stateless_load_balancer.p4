#define SERVERS 2

//-------------------- Headers ------------------------
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
header_type switch_info_t switch_info_head;

header_type meta_t {
    fields {
        temp_reg : 32;
    }
}
metadata meta_t meta;

//-----------------------------------------------------

//-------------------- Parsers ------------------------
parser start {
    return select(current(0, 64)) {
        0: parse_head;
        //1: interswitch;
        default: ingress;
    }
}

parser parse_head {
    extract(load_balancer_head);
    return ingress;
}

//-----------------------------------------------------

action _drop() {
    drop();
}

//------------------ Select Port -----------------------
register flow_count_register {
    width: 32;
    instance_count: 1;
}

action select_port() {
	register_read(meta.temp_reg, flow_count_register, 0);
    modify_field(standard_metadata.egress_spec, (meta.temp_reg % SERVERS)+2);
    add_to_field(meta.temp_reg, 1);
    register_write(flow_count_register,0,meta.temp_reg);
}

table select_port_table{
	actions{
		select_port;
	}
	size: 1;
}
//-------------------------------------------------------




//------------------------ Control Logic -----------------

control ingress {
    if(load_balancer_head.flags == 0x01){
    	apply(select_port_table);
    	apply()
    }
    apply(route_packet_table);
    if(load_balancer_head.flags == 0x02){
    	apply(clear_port);
    }
}

control egress {
}
