#!/usr/bin/python3
import socket
import sys

# Input IP address
ff = input("Enter IP: ")
ip = socket.gethostbyname(ff)
ip1 = ip.split('.')
base_ip = '.'.join(ip1[:3])

# Generate IP addresses
target_ips = []
for i in range(1, 255):
    target_ip = f"{base_ip}.{i}"
    target_ips.append(target_ip)

# List of ports to scan
ports = [80, 443, 7001]

# Scan ports for each IP address
try:
    for targ in target_ips:
        for port in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(1)
            result = s.connect_ex((targ, port))
            if result == 0:
                print(f"Port {port} is open on {targ}")
            s.close()
except KeyboardInterrupt:
    print("Exiting program")
except socket.gaierror:
    print("Host does not resolve")
    sys.exit()
except socket.error:
    print("Could not connect")
    sys.exit()

