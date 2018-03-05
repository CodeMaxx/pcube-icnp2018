rm -rf pcap pcap.zip
mkdir pcap
cp ../*.pcap pcap/
zip -r pcap.zip pcap/
python3 all_stats.py
