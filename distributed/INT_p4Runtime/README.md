# INT with controller using p4Runtime
- Implement Traffic Engineering using the below topology.
![INT p4Runtime Topolgy](./images/topology.jpg)
Here S2 is the bottleneck switch and the numbers on the each ports is the queue rate for that particular port. Once the queue depth crosses the threshold, the controller will dynamically adjust the egress port of the flow to load balance equally on all egress ports of the S2 switch.
- The contoller will burn the p4 program and install rules into the switches using p4Runtime API.
- How to run program
  ./run.sh to run the mininet and bring up program_switches
  make clean to clean up
  ./mycontoller.py to start the Controller
