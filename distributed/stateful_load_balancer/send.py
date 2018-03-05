#!/usr/bin/python

from scapy.all import sniff, sendp
from scapy.all import Packet
from scapy.all import IntField, LongField

import sys
from random import seed,uniform
import threading
from time import sleep

if len(sys.argv) < 2:
	print("./send.py <client ID>")
	exit(0)
HOSTNAME = int(sys.argv[1])
IFACE = "eth0"
FLOW_THRESHOLD = 10
MIN_SLEEP, MAX_SLEEP = 0.01,0.3
MIN_PACKET_NUM, MAX_PACKET_NUM = 4, 30
MIN_PACKET_LENGTH, MAX_PACKET_LENGTH = 1,20

seed(101)

class LoadBalancePkt(Packet):
	name = "LoadBalancePkt"
	fields_desc = [
		LongField("preamble", 0),
		IntField("syn", 0),
		IntField("fin", 0),
		IntField("fid",0),
		IntField("hash",0),
		IntField("count",0),
		IntField("swid", 0),
		IntField("flow_num", 0)
	]

class Flow(threading.Thread):

	def __init__(self, fid, delay):
		threading.Thread.__init__(self)
		self.fid = fid
		self.delay = delay

	def run(self):
		fid,delay = self.fid, self.delay

		payload = "SYN-" + str(fid)
		p = LoadBalancePkt(syn=1  , fid=fid) / payload
		print 'syn'+str(fid)
		print p.show()
		sleep(delay)
		sendp(p, iface = IFACE)

		# print(fid)
		for i in range(int(uniform(MIN_PACKET_NUM,MAX_PACKET_NUM))):
			payload = "Data-"+str(fid) + "-" + ((str(i)+'-')*int(uniform(MIN_PACKET_LENGTH,MAX_PACKET_LENGTH)))
			p = LoadBalancePkt(fid=fid) / payload
			print p.show()
			sleep(delay)
			sendp(p, iface = IFACE)

		payload = "FIN-" + str(fid)
		p = LoadBalancePkt(fin=1  , fid=fid) / payload
		print p.show()
		sleep(delay)
		sendp(p, iface = IFACE)

def main():
	flow_count = 0

	threadLock = threading.Lock()
	threads = []

	while flow_count != FLOW_THRESHOLD:
		try:
		   t = Flow(flow_count, uniform(MIN_SLEEP, MAX_SLEEP))
		   t.start()
		   threads.append(t)
		   flow_count+=1
		except:
		   print "Error: unable to start flow"

	for t in threads:
		t.join()

if __name__ == '__main__':
	main()
