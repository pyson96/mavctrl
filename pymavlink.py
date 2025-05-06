import socket
import sys
from pymavlink.dialects.v20 import common as mavlink2

mav = mavlink2.MAVLink(None)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 18570)) 
sock.settimeout(2.0)

try:
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            for byte in data:
                try:
                    msg = mav.parse_char(bytes([byte]))
                    if msg:
                        print(f"[{msg.get_type()}] {msg.to_dict()}\n")
                except mavlink2.MAVError as e:
                    print(f"Parse error: {e}")
        except socket.timeout:
            continue
except KeyboardInterrupt:
    print("\nStopped by user.")
    sys.exit(0)
