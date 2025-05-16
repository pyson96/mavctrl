import socket
import sys
import time
from pymavlink.dialects.v20 import common as mavlink2

# MAVLink 파서 및 UDP 소켓 설정
mav = mavlink2.MAVLink(None)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 14540))
sock.settimeout(2.0)

target_ip = '0.0.0.0'
target_port = 0
target_system = 1
target_component = 1

print("MAVLink 데이터를 수신 중입니다...")


def send_mavlink_command(command: int, param1=0, param2=0, param3=0, param4=0, param5=0, param6=0, param7=0):
    global target_system, target_component, target_ip, target_port

    msg = mav.command_long_encode(
        target_system,
        target_component,
        command,
        0,  # confirmation
        param1, param2, param3, param4,
        param5, param6, param7
    )
    sock.sendto(msg.pack(mav), (target_ip, target_port))
    print(f"MAVLink 명령 전송 완료: {command} → {target_ip}:{target_port}")


def send_arm():
    print("ARMING 명령 전송 중...")
    # param1 = 1 to arm, 0 to disarm
    send_mavlink_command(mavlink2.MAV_CMD_COMPONENT_ARM_DISARM, 1)

def send_takeoff():
    print("이륙 명령 전송 중...")
    send_mavlink_command(
        mavlink2.MAV_CMD_NAV_TAKEOFF,
        -1, 0, 0, float('nan'),  # 위도
        float('nan'), float('nan'), 498.106  # 고도 10m
    )


try:
    heartbeat_received = False

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            target_ip = addr[0]
            target_port = addr[1]

            for byte in data:
                try:
                    msg = mav.parse_char(bytes([byte]))
                    if not msg:
                        continue

                    msg_type = msg.get_type()

                    if msg_type == 'HEARTBEAT' and not heartbeat_received:
                        target_system = msg.get_srcSystem()
                        target_component = msg.get_srcComponent()
                        heartbeat_received = True

                        print(f"HEARTBEAT 수신됨 from {target_ip}:{target_port} — 3초 후 ARM → TAKEOFF 순서대로 명령 전송.")
                        for i in range(1, 4):
                            print(f"{i}초...")
                            time.sleep(1)

                        #send_arm()
                        #time.sleep(2)  # allow time for arming
                        send_takeoff()
                        send_arm()

                    # ✅ Only print ACK messages
                    elif msg_type == 'COMMAND_ACK':
                        print(f"[COMMAND_ACK] {msg.to_dict()}")

                except mavlink2.MAVError as e:
                    print(f"Parse error: {e}")

        except socket.timeout:
            continue

except KeyboardInterrupt:
    print("\n사용자에 의해 종료됨.")
    sys.exit(0)
