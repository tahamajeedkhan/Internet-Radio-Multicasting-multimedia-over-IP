import cv2
import time
import struct
import socket
import numpy as np
from select import select
from videoprops import get_video_properties

multicast_group = '224.1.1.1'
server_address = ('', 10000)

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(server_address)

    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

except socket.error as e:
    print(f"\n Socket Error Occurred: {e} \n")
    exit(1)    


try:
    props_1 = get_video_properties('example.mp4')
    width_1 = props_1['width']
    height_1 = props_1['height']
    Ratio_1 = props_1['display_aspect_ratio']
    Frame_1 = props_1['avg_frame_rate']

    props_2 = get_video_properties('Big_Bunny.mp4')

    width_2 = props_2['width']
    height_2 = props_2['height']
    Ratio_2 = props_2['display_aspect_ratio']
    Frame_2 = props_2['avg_frame_rate']

except Exception as e:
    print(f"\n Error Occurred while Getting Video Properties: {e}")
    exit(1)    

print("\n Server is Successfully Started")

try:
    data1, address = sock.recvfrom(10001)
except socket.error as e:
    print(f"\n Socket Error : {e} \n")
    sock.close()
    exit(1)        

print(f"\n --> Client Connected : {address} \n")

data1 = data1.decode()
choice = str(data1)

if(data1 != "start"):
    print("\n Can't Connect, Bye !!! \n")
    exit(1)        
else:
    input_value = ("example.mp4" + "," + str(width_1) + "," + str(height_1) + "," + str(Ratio_1) + "," + str(Frame_1) + "," + "Big_Bunny.mp4" + "," + str(width_2) + "," + str(height_2) + "," + str(Ratio_2) + "," + str(Frame_2))
    input_value = input_value.encode()

    try:
        sock.sendto(input_value, (multicast_group, 10001))
    except socket.error as e:
        print("\n Socket Error \n")
        exit(1)

    data, address = sock.recvfrom(65535) 
    data = data.decode()

    choice = str(data)

    if(len(choice) > 1):
        print("\n Kindly, Restart Server for New Client \n")
        exit(1)

    print(f"\n initial : User Selected Station - {choice}")

    if(choice == '1'):
        cap = cv2.VideoCapture('example.mp4')
    elif(choice == '2'):
        cap = cv2.VideoCapture('Big_Bunny.mp4')        
    else:
        print("\n No Station Selected \n")
        exit(1)

    FPS = 30
    inpv = 5
    timeout = 0.0001

    while True:
        try:
            ready, _, _ = select([sock], [], [], timeout)
        except:
            print("\n Program Terminated \n")    
            exit(1)

        if ready:
            try:
                inpv = ''
                inpv, address = sock.recvfrom(65535)

                data = str(inpv)

                if not inpv:
                    break
                
                if(len(inpv) > 1):
                    print("\n\n Terminating ... \n")
                    print("\n --> Try to Restart the Server \n")
                    exit(1)
                inpv = inpv.decode()

                print(f"\n updated : User Selected Station - {inpv}")

                if inpv == '1':
                    cap = cv2.VideoCapture('example.mp4')
                elif inpv == '2':
                    cap = cv2.VideoCapture('Big_Bunny.mp4')

            except socket.error as e:
                print(f"\n Socket Error Occurred: {e} \n")
                exit(1)  

        try:
            ret, frame = cap.read()

            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            data = cv2.imencode('.jpg', frame)[1].tobytes()

            sock.sendto(data, (multicast_group, 10001))

            send_time = time.time()

            time.sleep(1/FPS - (time.time() - send_time))

        except KeyboardInterrupt:
            sock.close()
            break