#ifndef __INT_DEFINE__
#define __INT_DEFINE__



/* indicate INT at LSB of DSCP */
const bit<6> INT_DSCP = 0x1;
#define ETH_TYPE_IPV4 0x0800
#define IP_PROTO_TCP 8w6
const bit<8> INT_HEADER_LEN_WORD = 4;
const bit<8> REMAINING_HOP_CNT = 3;
typedef bit<48> macAddr_t;


#endif
