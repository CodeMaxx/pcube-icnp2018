import json
from collections import OrderedDict

def read_topo():
    nb_hosts = 0
    nb_switches = 0
    links = []
    with open("topo.txt", "r") as f:
        line = f.readline()[:-1]
        w, nb_switches = line.split()
        assert(w == "switches")
        line = f.readline()[:-1]
        w, nb_hosts = line.split()
        assert(w == "hosts")
        for line in f:
            if not f: break
            a, b = line.split()
            links.append( (a, b) )

    json_data = OrderedDict()
    json_data["nb_switches"], json_data["nb_hosts"] = nb_switches, nb_hosts

    json_data["links"] = OrderedDict()
    for i in range(0,len(links)):
        connection = OrderedDict()
        connection["_0"], connection["_1"] = links[i][0], links[i][1]
        json_data["links"]["_%d"%i] = connection

    return json_data

data = read_topo()
with open('topo.json', 'w') as out:
    json.dump(data, out, indent=4)

