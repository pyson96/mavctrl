from pymavlink import mavutil

connection_string = 'udp:0.0.0.0:18570'

master = mavutil.mavlink_connection(connection_string)

print("Waiting for heartbeat...")
master.wait_heartbeat()
print(f"Heartbeat from system (system {master.target_system}, component {master.target_component})")

try:
    while True:
        msg = master.recv_match(blocking=True)
        if msg:
            print(f"[{msg.get_type()}] {msg.to_dict()}")
except KeyboardInterrupt:
    print("Stopped by user.")
