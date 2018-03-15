// this is a common file which contains some control functions which are imported both in int_source as well as int_transit files
/********************************************************************
* int_transit_source_common.p4: tables, actions, and control flow
*******************************************************************/
#include <core.p4>
#include <v1model.p4>
#include "includes/headers.p4"
#include "includes/parser.p4"
#include "includes/checksums.p4"


control Int_metadata_insert(inout headers hdr, in int_metadata_t int_metadata,inout standard_metadata_t standard_metadata)
{
        /* this reference implementation covers only INT instructions 0-3 */
        action int_set_header_0() {
            hdr.int_switch_id.setValid();
            hdr.int_switch_id.switch_id = int_metadata.switch_id;
        }
        action int_set_header_1() {
            hdr.int_port_ids.setValid();
            hdr.int_port_ids.ingress_port_id =
                (bit<16>) standard_metadata.ingress_port;
            hdr.int_port_ids.egress_port_id =
                (bit<16>) standard_metadata.egress_port;
        }
        action int_set_header_2() {
            hdr.int_hop_latency.setValid();
            hdr.int_hop_latency.hop_latency =
                (bit<32>) standard_metadata.deq_timedelta;
        }
        action int_set_header_3() {
            hdr.int_q_occupancy.setValid();
            hdr.int_q_occupancy.q_id =
                (bit<8>) standard_metadata.egress_rid;
            hdr.int_q_occupancy.q_occupancy =
                (bit<24>) standard_metadata.deq_qdepth;
        }
        /* action functions for bits 0-3 combinations, 0 is msb, 3 is lsb */
        /* Each bit set indicates that corresponding INT header should be added */
        action int_set_header_0003_i0() {
        }
        action int_set_header_0003_i1() {
            int_set_header_3();
        }
        action int_set_header_0003_i2() {
            int_set_header_2();
        }
        action int_set_header_0003_i3() {
            int_set_header_3();
            int_set_header_2();
        }
        action int_set_header_0003_i4() {
            int_set_header_1();
        }
        action int_set_header_0003_i5() {
            int_set_header_3();
            int_set_header_1();
        }
        action int_set_header_0003_i6() {
            int_set_header_2();
            int_set_header_1();
        }
        action int_set_header_0003_i7() {
            int_set_header_3();
            int_set_header_2();
            int_set_header_1();
        }
        action int_set_header_0003_i8() {
            int_set_header_0();
        }
        action int_set_header_0003_i9() {
            int_set_header_3();
            int_set_header_0();
        }
        action int_set_header_0003_i10() {
            int_set_header_2();
            int_set_header_0();
        }
        action int_set_header_0003_i11() {
            int_set_header_3();
            int_set_header_2();
            int_set_header_0();
        }
        action int_set_header_0003_i12() {
            int_set_header_1();
            int_set_header_0();
        }
        action int_set_header_0003_i13() {
            int_set_header_3();
            int_set_header_1();
            int_set_header_0();
        }
        action int_set_header_0003_i14() {
            int_set_header_2();
            int_set_header_1();
            int_set_header_0();
        }
        action int_set_header_0003_i15() {
            int_set_header_3();
            int_set_header_2();
            int_set_header_1();
            int_set_header_0();
        }
        /* Table to process instruction bits 0-3 */
        table int_inst_0003 {
            key = {
                hdr.int_header.instruction_mask_0003 : exact;
            }
            actions = {
            /*    int_set_header_0;
                int_set_header_1;
                int_set_header_2;
                int_set_header_3; */
                int_set_header_0003_i0;
                int_set_header_0003_i1;
                int_set_header_0003_i2;
                int_set_header_0003_i3;
                int_set_header_0003_i4;
                int_set_header_0003_i5;
                int_set_header_0003_i6;
                int_set_header_0003_i7;
                int_set_header_0003_i8;
                int_set_header_0003_i9;
                int_set_header_0003_i10;
                int_set_header_0003_i11;
                int_set_header_0003_i12;
                int_set_header_0003_i13;
                int_set_header_0003_i14;
                int_set_header_0003_i15;
            }
            default_action = int_set_header_0003_i0();
            //default_action=int_set_header_0();
            size = 16;
        }

        /* Similar tables can be defined for instruction bits 4-7 and bits 8-11 */
        /* e.g., int_inst_0407, int_inst_0811 */

        apply{
            int_inst_0003.apply();
            // int_inst_0407.apply();
            // int_inst_0811.apply();
        }
}
control Int_outer_encap(inout headers hdr, in int_metadata_t int_metadata)
{
        action int_update_ipv4() {
            hdr.ipv4.totalLen = hdr.ipv4.totalLen + int_metadata.insert_byte_cnt;
        }
        action int_update_shim() {
            hdr.intl4_shim.len = hdr.intl4_shim.len + int_metadata.int_hdr_word_len;
        }
        apply{
            if (hdr.ipv4.isValid()) {
            int_update_ipv4();
            }
        /* Add: UDP length update if you support UDP */


        if (hdr.intl4_shim.isValid()) {
            int_update_shim();
        }
    }
}
/* TBD - Check egress link MTU, do not insert any metadata and
set M bit if adding metadata will cause egress MTU to be exceeded */
control Int_transit_egress(inout headers hdr, inout metadata meta,
inout standard_metadata_t standard_metadata)
{
        action int_transit(bit<32> switch_id) {
            meta.int_metadata.switch_id = switch_id;
            meta.int_metadata.insert_byte_cnt = (bit<16>) hdr.int_header.ins_cnt << 2;
            meta.int_metadata.int_hdr_word_len = (bit<8>) hdr.int_header.ins_cnt;
        }
        table int_prep {
            key = {}
            actions = {int_transit;}
        }
        Int_metadata_insert() int_metadata_insert;
        Int_outer_encap() int_outer_encap;
        action int_hop_cnt_decrement() {
            hdr.int_header.remaining_hop_cnt =
            hdr.int_header.remaining_hop_cnt - 1;
        }
        action int_hop_cnt_exceeded() {
            hdr.int_header.e = 1;
        }

        apply{
            if(hdr.int_header.isValid()) {
                if(hdr.int_header.remaining_hop_cnt != 0 && hdr.int_header.e == 0) {
                    int_hop_cnt_decrement();
                    int_prep.apply();
                    int_metadata_insert.apply(hdr, meta.int_metadata, standard_metadata);
                    int_outer_encap.apply(hdr, meta.int_metadata);
                }
                else {
                    int_hop_cnt_exceeded();
                }
            }
        }
}
