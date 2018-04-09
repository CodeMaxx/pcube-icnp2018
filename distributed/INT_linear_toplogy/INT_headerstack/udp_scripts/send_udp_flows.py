import client
import threading
from datetime import datetime
#elephant flows
total_packets_sent_thread1 = 0
total_packets_sent_thread2 = 0

num_threads = 2;
class UDPFlow(threading.Thread):
	def __init__(self,threadID):
		threading.Thread.__init__(self)
		self.created_at = datetime.now()
		self.threadID = threadID

	def run(self):
		global total_packets_sent_thread1
		global total_packets_sent_thread2
		threadID = self.threadID
		if threadID == 0 :
			# num_elephant_flows = 60
			num_elephant_flows = 45
			no_of_bytes_to_send = 1370
			total_exp_time = 450
			elecphant_flow_time = 10
			total_packets_sent_elephant = 0
			for SOURCE_PORT in range(7011,7011+num_elephant_flows):
				# print ("Sending elephant_flow using Source_port : ",SOURCE_PORT)
				# total_packets_sent_elephant += client.send_data(elecphant_flow_time,no_of_bytes_to_send,SOURCE_PORT)
				total_packets_sent_thread1 += client.send_data(elecphant_flow_time,no_of_bytes_to_send,SOURCE_PORT)
			print("total_packets_sent_thread1 = ",total_packets_sent_thread1)
			# print ("total_packets_sent_elephant = ",total_packets_sent_elephant)
		# if threadID in range(1,11):
		if threadID == 1:
			num_mouse_flows = 450
			no_of_bytes_to_send = 10
			mouse_flow_time = 0.1
			total_packets_sent_mouse = 0
			upto = 50000+(num_mouse_flows*10)
			for SOURCE_PORT in range(50000,upto):
				if SOURCE_PORT > 50449:
					SOURCE_PORT = 50000+SOURCE_PORT%num_mouse_flows
				# print ("Sending mouse_flow using Source_port : ",SOURCE_PORT)
				# total_packets_sent_mouse += client.send_data(mouse_flow_time,no_of_bytes_to_send,SOURCE_PORT)
				total_packets_sent_thread2 += client.send_data(mouse_flow_time,no_of_bytes_to_send,SOURCE_PORT)
			print("total_packets_sent_thread2 = ",total_packets_sent_thread2)


			# print ("total_packets_sent_mouse = ",total_packets_sent_mouse)

def start_threads():
	threads = []
	for i in range(num_threads):
		try:
			t = UDPFlow(i)
			t.start()
			threads.append(t)
		except:
		   print("Error: unable to start flow")

	for t in threads:
		t.join()
	

def main():
	experiment_start = datetime.now()
	print("experiment starts at ",datetime.now())
	start_threads()
	print("total packets sent overall = ",total_packets_sent_thread1+total_packets_sent_thread1)
	experiment_ends = datetime.now()
	print("toatl time taken = ", (experiment_ends-experiment_start).total_seconds())

if __name__ == '__main__':
	main()
