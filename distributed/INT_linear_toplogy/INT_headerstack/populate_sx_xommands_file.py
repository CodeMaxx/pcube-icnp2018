
num_elephant_flows = 59
# populate in s1-s6 files the following entries
# table_add ipv4_lpm ipv4_forward 10.0.1.1/32 8080 7070 => 00:00:00:00:01:01 1
# table_add ipv4_lpm ipv4_forward 10.0.8.2/32 7070 8080 => 00:00:00:00:08:02 2
# 7070 is src SOURCE_PORT
for i in range(1,9):
	file_to_open = "s"+str(i)+"-commands.txt"
	print ("file_to_open = ", file_to_open)
	f1 = open(file_to_open,'a')

	for SOURCE_PORT in range(7011,7011+num_elephant_flows):
		if i == 7:
			command_to_write1 = "table_add ipv4_lpm ipv4_forward 10.0.1.1/32 8080 "+str(SOURCE_PORT)+" => 00:00:00:00:01:01 1"
			command_to_write2 = "table_add ipv4_lpm ipv4_forward 10.0.8.2/32 "+str(SOURCE_PORT)+" 8080 => 00:00:00:00:08:02 5"
		elif i == 8 :
			command_to_write1 = "table_add ipv4_lpm ipv4_forward 10.0.1.1/32 8080 "+str(SOURCE_PORT)+" => 00:00:00:00:01:01 2"
			command_to_write2 = "table_add ipv4_lpm ipv4_forward 10.0.8.2/32 "+str(SOURCE_PORT)+" 8080 => 00:00:00:00:08:02 1"
		# i= 1 to 6
		else :
			command_to_write1 = "table_add ipv4_lpm ipv4_forward 10.0.1.1/32 8080 "+str(SOURCE_PORT)+" => 00:00:00:00:01:01 1"
			command_to_write2 = "table_add ipv4_lpm ipv4_forward 10.0.8.2/32 "+str(SOURCE_PORT)+" 8080 => 00:00:00:00:08:02 2"
		#print ("command to write = ", command_to_write1)
		#print ("command to write = ", command_to_write2)
		f1.write(command_to_write1)
		f1.write("\n")
		f1.write(command_to_write2)
		f1.write("\n")
	f1.close()