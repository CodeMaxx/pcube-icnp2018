#!/usr/bin/env python3

from scapy.all import sniff, sendp
from scapy.all import Packet
from scapy.all import IntField, LongField

import sys
from random import seed,uniform,choice
import threading
from time import sleep

from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

if len(sys.argv) < 3:
	print("./send.py <client ID> <Experiment Time in seconds>")
	exit(0)

HOSTNAME = int(sys.argv[1])
total_exp_time = int(sys.argv[2])

IFACE = "eth0"
THREAD_THRESHOLD = 50
MIN_SLEEP, MAX_SLEEP = 0.0, 0.3
MIN_PACKET_NUM, MAX_PACKET_NUM = 28, 30
MIN_PACKET_LENGTH, MAX_PACKET_LENGTH = 5,20
CHANGE_FREQUENCY = 20
experiment_starts = datetime.now()
num_threads = 30
np.random.seed(0)
thread_sleep = [0,10]
globals()["probabilities"] = [0.95,0.05]
seed(101)

class LoadBalancePkt(Packet):
	name = "LoadBalancePkt"
	fields_desc = [
		LongField("preamble", 0),
		IntField("syn", 0),
		IntField("fin", 0),
		IntField("fid",0),
		IntField("subfid",0),
		IntField("packet_id",0),
		IntField("hash",0),
		IntField("count",0),
		IntField("swid", 0),
		IntField("flow_num", 0)
	]

class Flow(threading.Thread):

	def __init__(self, fid):
		threading.Thread.__init__(self)
		self.fid = fid
		self.created_at = datetime.now()
		self.modified_at = datetime.now()

	def run(self):
		fid = self.fid
		subfid = 0
		change_frequency = CHANGE_FREQUENCY 
		means = [0.0001, 0.001]
		mean = choice(means)
		experiment_starts_timestamp = experiment_starts.timestamp()

		log = open('timelog/' + str(fid) + '.log', 'w')

		while (datetime.now() - experiment_starts).total_seconds() < total_exp_time:
	

			subfid += 1
			time_gone = datetime.now() - self.modified_at
			if(time_gone.total_seconds() > total_exp_time/change_frequency):
			# if(time_gone.total_seconds() > change_frequency):
				globals()["probabilities"].reverse()
				self.modified_at = datetime.now()
				mean = choice(means)

			sleep(np.random.choice(thread_sleep, p=globals()["probabilities"]))

			delay = 0
			while delay <= 0:
				delay = np.random.normal(mean, 0.1*mean)

			payload = "SYN-" + str(fid) + "-" + str(subfid)
			p = LoadBalancePkt(syn=1, fid=fid, subfid=subfid, packet_id=0) / payload
			print('syn'+str(fid) + "-" + str(subfid))
			p.show()
			sleep(delay)
			sendp(p, iface = IFACE)
			log.write(str(datetime.now().timestamp() -
                            experiment_starts_timestamp) + " %d %d %d\n"%(1,fid,subfid))

			# print(fid)
			for i in range(int(uniform(MIN_PACKET_NUM,MAX_PACKET_NUM))):
				payload = "Data-" + str(fid) + "-" + str(subfid) + '-' + ((str(i)+'-')*int(uniform(MIN_PACKET_LENGTH,MAX_PACKET_LENGTH)))
				p = LoadBalancePkt(fid=fid, subfid=subfid, packet_id=i) / payload
				p.show()
				sleep(delay)
				sendp(p, iface = IFACE)
				log.write(str(datetime.now().timestamp() - experiment_starts_timestamp) + " %d %d %d\n"%(0,fid,subfid))

			payload = "FIN-" + str(fid) + "-" + str(subfid)
			p = LoadBalancePkt(fin=1, fid=fid, subfid=subfid, packet_id=i) / payload
			p.show()
			sleep(delay)
			sendp(p, iface = IFACE)
			log.write(str(datetime.now().timestamp() - experiment_starts_timestamp) + " %d %d %d\n"%(2,fid,subfid))
		
		log.close()

def draw_histogram():
	x = []
	syn,fin = [], []
	fmap = {}
	for i in range(num_threads):
		fid = (HOSTNAME * THREAD_THRESHOLD) + i
		with open("timelog/" + str(fid) + '.log') as f:
			for row in f:
				time,index,fid,subfid = row.split()
				time,index = float(time), int(index)
				x.append(time)
				if index == 1: 
					syn.append(time)
					fmap[(fid,subfid)] = {'syn':time}
				elif index == 2: 
					fin.append(time)
					fmap[(fid,subfid)]['fin'] = time

	x.sort()
	flow_rate,STEP = [], 0.5
	flow_rate_smooth = []
	for i in np.arange(0,int(x[-1])+1,STEP):
		fcount = 0
		for k in fmap:
			if fmap[k]['syn'] < i and fmap[k]['fin'] >i:
				fcount += 1
				flow_rate_smooth.append(i)
		flow_rate.append(fcount)

	pd.DataFrame(x).plot(kind='density',figsize=(total_exp_time,1))
	for s in syn: plt.axvline(s,color='r')
	for f in fin: plt.axvline(f,color='g')
	ax = plt.gca()
	ax.set_xlim((x[0],x[-1]))
	plt.ylabel('Percentage')
	plt.show()
	# savefig('packets_%s_%s.png'%(num_threads,CHANGE_FREQUENCY), bbox_inches='tight')

	pd.DataFrame(x).plot(kind='density')
	plt.show()

	plt.plot(np.arange(0,int(x[-1])+1,STEP),flow_rate)
	ax = plt.gca()
	ax.set_ylim((0,num_threads+2))
	plt.show()

def start_threads():
	threadLock = threading.Lock()
	threads = []

	for i in range(num_threads):
		try:
			t = Flow((HOSTNAME * THREAD_THRESHOLD) + i)
			t.start()
			threads.append(t)
		except:
		   print("Error: unable to start flow")

	for t in threads:
		t.join()

def main():
	start_threads()
	draw_histogram()

if __name__ == '__main__':
	main()