import socket
import select
import ipaddress
import threading
import time
from mcstatus import JavaServer

def port_scanner(ip, port, valid_ips):
 with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
     sock.settimeout(1)
     try:
         sock.connect((str(ip), port))
         print(f"VALID IP IS {ip}")
         valid_ips.append(ip)
         return ip
     except:
         return None

def ip_generator(start_ip, end_ip):
 for ip in ipaddress.summarize_address_range(start_ip, end_ip):
     for address in ip:
         yield address

def cleanup_threads(sockets_list):
 # Remove completed threads from the list
 sockets_list[:] = [t for t in sockets_list if t.is_alive()]

def get_mc_status(ip_list, file):#called after ip's are found, cannot be done with multithreading.
 for ip in ip_list:
     server = JavaServer.lookup(str(ip), 25565)
     status = server.status()
     file.write(f"The server {ip} is running {status.version.name} ; {status.players.online} player(s) online out of {status.players.max} | {status.motd.to_plain()}\n")

start_ip = ipaddress.IPv4Address('70.0.0.0')
end_ip = ipaddress.IPv4Address('71.0.0.0')

valid_ips = []
sockets_list = []
cleanup_interval = 1000 # Adjust the cleanup interval as needed

try:
   for ip in ip_generator(start_ip, end_ip):
       t = threading.Thread(target=port_scanner, args=(ip, 25565, valid_ips))
       t.start()
       sockets_list.append(t)

       # Periodically cleanup the threads list
       if len(sockets_list) % cleanup_interval == 0:
           cleanup_threads(sockets_list)

   # Cleanup remaining threads after finishing the loop
   cleanup_threads(sockets_list)

   # Wait for all threads to complete before exiting
   for t in sockets_list:
       t.join()

finally:
   # Now that we have the list of valid IPs, we can get the Minecraft server status
   with open('open_ports25565.txt', 'w') as f:
       get_mc_status(valid_ips, f)
