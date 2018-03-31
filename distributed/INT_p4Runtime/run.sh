mkdir -p build pcaps logs
p4c-bm2-ss --p4v 16 --p4runtime-file build/int_transit.p4info --p4runtime-format text -o build/int_transit.json int_transit.p4
p4c-bm2-ss --p4v 16 --p4runtime-file build/int_source.p4info --p4runtime-format text -o build/int_source.json int_source.p4
p4c-bm2-ss --p4v 16 --p4runtime-file build/int_sink.p4info --p4runtime-format text -o build/int_sink.json int_sink.p4
make
