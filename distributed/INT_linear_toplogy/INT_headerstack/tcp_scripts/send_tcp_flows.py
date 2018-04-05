import client

#elephant flows

num_elephant_flows = 60
no_of_bytes_to_send = 1370
total_exp_time = 600
elecphant_flow_time = 10
for SOURCE_PORT in range(7011,7011+num_elephant_flows):
	print ("Sending using Source_port : ",SOURCE_PORT)
	client.send_data(elecphant_flow_time,no_of_bytes_to_send,SOURCE_PORT)