import decision_time
import data_forwarding_time
import num_probe_packets
import link_traffic

from utils import *

def main():
    cprint("STATISTICS")
    decision_time.main()
    data_forwarding_time.main()
    num_probe_packets.main()
    link_traffic.main()

if __name__ == '__main__':
    main()
