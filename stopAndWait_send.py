import socket
import os
import hashlib
import threading
import struct





class Sender():
    def __init__(self,ip,port,n):
        self.ip = ip
        self.port = port

        self.max_seq_num = 2 ** n
        #self.seq_num = 0

        self.window_size = self.max_seq_num
        self.window = list() #1개씩만들어가도록 해야한다. 실제 패킷이 들어가는 부분
        self.window_seq = list() #seq_num이 들어가는 부분

        self.send_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.send_socket.settimeout(5)

        self.file_name = None
        self.file_size = 0
        self.file_pointer = self.read_file()
        self.file_send_cur_size = 0

        self.count=0


        self.lock = threading.Lock()

    def go_back_N(self):
        self.send_header()
        self.print_cur_size()
        self.fill_window()


        while self.file_send_cur_size <self.file_size:
            self.send_packets()
            self.recv_ack()
            self.print_cur_size()
        self.send_packets()


        self.print_cur_size()


    def send_packets(self):
        try:

            packet = self.window[0]
            self.send(packet)
        except Exception as e:
            pass


    def recv_ack(self):
        try:
            recv = self.recv()
            split_recv = recv.split(' ')
            if split_recv[0] == 'ACK':
                seq_num = int(split_recv[1])

                print(recv, "send_num", seq_num)
                self.update_window(seq_num)
                self.print_window()
        except socket.timeout:
            print("*************TIMEOUT OCCUR***************")
            #self.window_sent.clear()
            return

    #def check_sent_packet(self):
    #    to_send = list()
    #    print("WINDOW_SENT",len(self.window_sent))
        #print("WINDOW",self.window)
    #    for packet in self.window:
    #        if not packet in self.window_sent:
    #            to_send.append(packet)
    #    return to_send


    def make_packet(self, seq_num):
        try:
            payload_data = self.file_pointer.read(1024)
            if payload_data == b'':
                print("close")
                self.file_pointer.close()
                return None
            packet = self.pack(payload_data, 'd', seq_num)
            return packet
        except ValueError as e:
            print("close(file)")
            return None

    def update_window(self,seq_num):
        self.print_window()
        #buffer_index = self.window_seq.index(seq_num)
        print("seq_num", seq_num)

        packets = self.window[0]
        del self.window[0]
        del self.window_seq[0]


        packet = self.make_packet(seq_num)
        if packet is  None:
            return

        self.window.append(packet)
        self.window_seq.append(seq_num)
            #self.window_sent.append(False)







            #self.update_seq_num()

    def print_window(self):
        for i in range(len(self.window_seq)):
            if i == 0:
                print("CURRENT - WINDOW : [", self.window_seq[0], end = ' ')
            else:
                print(', '+str(self.window_seq[i]), end = ' ')
        print("]")


    def print_cur_size(self):
        print("CUR SIZE / TOTAL SIZE = {0} / {1} , {2} %".\
        format(self.file_send_cur_size, self.file_size,\
        self.file_send_cur_size/self.file_size*100))













    def read_file(self):
        while True:
            file_name = input("input file name:")
            if os.path.isfile(file_name):
                self.file_name = file_name
                self.file_size = os.path.getsize(file_name)
                #print("Size",self.file_size)
                break
            else:
                print("No File exist")

        open_files = open(file_name,'rb')
        return open_files

    def send(self, data):
        self.send_socket.sendto(data, (self.ip,self.port))

    def recv(self):
        data, addr= self.send_socket.recvfrom(1024)
        return data.decode('utf-8')

    def checksum(self,data):
        hashing = hashlib.sha1()
        hashing.update(data)
        return hashing.digest()

    def pack(self, data, type, seq_num):
        format = None
        if type == 'i':
            type = type.encode()
            file_size = self.file_size.to_bytes(20, byteorder = "big")
            #print(self.file_size)
            file_name = self.file_name.ljust(20).encode()
            #print(self.checksum(type+file_size+file_name+data))
            checksum = struct.pack("20s",self.checksum(type+file_size+file_name+data))
            #print(checksum)
            format = type + file_size + file_name + checksum + data
        elif type =='d':
            type = type.encode()
            current_length = len(data).to_bytes(20, byteorder = "big")
            seq_num = seq_num.to_bytes(20, byteorder = "big")
            checksum = struct.pack("20s",self.checksum(type+current_length+seq_num+data))
            self.file_send_cur_size += len(data)

            format = type + current_length + seq_num + checksum +data
        else:
            format = None
        return format



    def send_header(self):
        while True:
            try:
                data = self.file_pointer.read(1024)
                self.file_send_cur_size += len(data)
                header = self.pack(data, 'i', 0)
                self.send(header)
                data = self.recv()

                if data == 'ACK':
                    print("Header Transmit Success")
                    print("Now Payload Transmit Start")
                    break

            except socket.timeout:
                print("TIME OUT OCCUR")
                print("TRANSMIT FIRST DATA AGAIN")

    def fill_window(self):
        seq_num = 0

        for i in range(self.window_size):
            packet = self.make_packet(seq_num)
            if packet is None:
                break
            self.window.append(packet)
            self.window_seq.append(seq_num)



    def main(self):
        self.go_back_N()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', type=str,
                        default='localhost')
    parser.add_argument('-p', '--port', type=int,
                        default=8000)
    parser.add_argument('-f', type=str)
    FLAGS, _ =parser.parse_known_args()
    send = Sender(FLAGS.ip, FLAGS.port,0)
    send.main()
