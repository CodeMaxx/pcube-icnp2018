

CREATE_GROUP = "mc_mgrp_create %d"
CREATE_NODE = "mc_node_create %d %d"
ASSOCIATE_NODE = "mc_node_associate %d %d"
MIRRORING_ADD = "mirroring_add %d %d"

NB_SWITCHES, NB_HOSTS = None, None

def get_data():
	with open('topo.json','r') as f:
		data = json.load(f)
	NB_SWITCHES = int(data.pop("nb_switches")) 
	NB_HOSTS = int(data.pop("nb_hosts"))
	links = []
	for k in data:
		a, b = str(data[k]["_0"]), str(data[k]["_1"])  
		links.append( (a,b) )

def print_mirroring_add():

## need to create a multicast group for each switch according to the connections, need to consider the servers it is connected to too 