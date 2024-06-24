import tkinter as tk
import socket
import struct
import numpy as np
import threading
import cv2

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Client GUI")
        self.connected = False
        
        self.create_widgets()
        
    def create_widgets(self):
        tk.Label(self.root, text="Client Status:").pack()
        self.client_status = tk.Label(self.root, text="Client not connected")
        self.client_status.pack()
        
        tk.Button(self.root, text="Connect", command=self.connect_to_server).pack(pady=10)
        self.disconnect_button = tk.Button(self.root, text="Disconnect", command=self.disconnect_from_server, state=tk.DISABLED)
        self.disconnect_button.pack()
        
        tk.Label(self.root, text="Select Station:").pack()
        self.station_var = tk.StringVar()
        self.station_var.set("1")
        self.station_selection = tk.Frame(self.root)
        self.station_selection.pack()
        station_options = [("Station 1", "1"), ("Station 2", "2")]
        for text, value in station_options:
            tk.Radiobutton(self.station_selection, text=text, variable=self.station_var, value=value, state=tk.DISABLED).pack(anchor='w')
        
        tk.Button(self.root, text="Start Stream", command=self.start_stream, state=tk.DISABLED).pack(pady=10)
        
        tk.Label(self.root, text="Video Feed:").pack()
        self.video_feed_label = tk.Label(self.root)
        self.video_feed_label.pack()
        
    def connect_to_server(self):
        if not self.connected:
            self.thread = threading.Thread(target=self.connect_and_receive)
            self.thread.start()
        else:
            self.client_status.config(text="Already connected")

    def disconnect_from_server(self):
        if self.connected:
            self.client_status.config(text="Disconnected")
            self.disconnect_button.config(state=tk.DISABLED)
            self.disable_station_selection()
            self.connected = False
            # Add code to disconnect from server
            self.sock.close()
            cv2.destroyAllWindows()  # Close OpenCV window
        else:
            self.client_status.config(text="Already disconnected")

    def enable_station_selection(self):
        self.station_var.set("1")
        for widget in self.station_selection.winfo_children():
            widget.config(state=tk.NORMAL)
        self.root.children['!button3'].config(state=tk.NORMAL)

    def disable_station_selection(self):
        for widget in self.station_selection.winfo_children():
            widget.config(state=tk.DISABLED)
        self.root.children['!button3'].config(state=tk.DISABLED)

    def start_stream(self):
        selected_station = self.station_var.get()
        print(f"Selected Station: {selected_station}")

        if selected_station == "1":
            self.play_video("Station 1")
        elif selected_station == "2":
            self.play_video("Station 2")

    def play_video(self, station_name):
        cap = cv2.VideoCapture(0)  # Open the default camera (or change the index for other cameras)
        cv2.namedWindow(station_name, cv2.WINDOW_NORMAL)

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(f'{station_name}_output.avi', fourcc, 20.0, (640, 480))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow(station_name, frame)
            out.write(frame) 

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()

    def connect_and_receive(self):
        multicast_group = '224.1.1.1'
        client_address = ('', 10001)

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(client_address)

            group = socket.inet_aton(multicast_group)
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65535)

            inp = 'start'
            self.sock.sendto(inp.encode(), (multicast_group, 10000))
            data, address = self.sock.recvfrom(10000)

            data = data.decode()
            n1, a, b, c, d, n2, e, f, g, h = data.split(',')

            self.client_status.config(text="Connected")
            self.connected = True
            self.disconnect_button.config(state=tk.NORMAL)
            self.enable_station_selection()

        except Exception as e:
            print(f"Error: {e}")

def main():
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
