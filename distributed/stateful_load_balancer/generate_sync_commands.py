import json

CREATE_GROUP = "mc_mgrp_create %d\n"
CREATE_NODE = "mc_node_create %d %d\n"
ASSOCIATE_NODE = "mc_node_associate %d %d\n"
MIRRORING_ADD = "mirroring_add %d %d\n"

NB_SWITCHES, NB_HOSTS = None, None

def get_data():
    with open('topo.json','r') as f:
        data = json.load(f)
    NB_SWITCHES = int(data.pop("nb_switches"))
    NB_HOSTS = int(data.pop("nb_hosts"))
    topo_stats = {}
    data = data["links"]
    for key in data:
        link = data[key]
        a, b = link["_0"], link["_1"]
        if a.startswith("s") and b.startswith("s"):
            try:
                topo_stats[a]["num_switches"] += 1
            except:
                topo_stats[a] = {"num_hosts": 0, "num_switches": 1}
            try:
                topo_stats[b]["num_switches"] += 1
            except:
                topo_stats[b] = {"num_hosts": 0, "num_switches": 1}
        elif a.startswith("s"):
            try:
                topo_stats[a]["num_hosts"] += 1
            except:
                topo_stats[a] = {"num_hosts": 1, "num_switches": 0}
        elif b.startswith("s"):
            try:
                topo_stats[b]["num_hosts"] += 1
            except:
                topo_stats[b] = {"num_hosts": 1, "num_switches": 0}

    return topo_stats

def generate_sync_commands(topo_stats):
    f = open("sync_commands.txt", "w")
    mgrp_no = 1
    node_no = 1
    max_port = 0
    for key in topo_stats:
        stat = topo_stats[key]
        num_hosts = stat["num_hosts"]
        num_switches = stat["num_switches"]
        total_ports = num_hosts + num_switches
        f.write(CREATE_GROUP % mgrp_no)
        for i in range(1, num_switches + 1):
            f.write(CREATE_NODE % (node_no, num_hosts + i))
            f.write(ASSOCIATE_NODE % (mgrp_no, node_no))
            node_no += 1
        if total_ports > max_port:
            max_port  = total_ports
        mgrp_no += 1
    for i in range(1, max_port + 1):
        f.write(MIRRORING_ADD % (i, i))
    f.close()


if __name__ == '__main__':
    topo_stats = get_data()
    generate_sync_commands(topo_stats)