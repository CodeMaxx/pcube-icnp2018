import socket, threading
# it gives more throughput as compared to server_multithreaded 
UDP_IP = "10.0.8.2"
# UDP_IP = "0.0.0.0"
UDP_PORT = 8080
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((UDP_IP, UDP_PORT))
print("Server started on " ,(UDP_IP, UDP_PORT))
print("Waiting for client request..")
total_packets_received = 0;
while True:
    data,address = server.recvfrom(2048)
    #print ("data bytes received =", data)
    msg = data.decode()
    total_packets_received +=1
    if msg=='bye':
        print("last packet from ", address)
        print( " bye received from client")  
        # break
        #print ("from client", msg)
    # y = server.sendto(bytes(msg,'UTF-8'),address)
    # print("y =",y)
print ("total_packets_received in this flow = ",total_packets_received)
    
