import socket
import struct
import time
import hashlib

class receiver():
    def __init__(self,FLAGS,files):
        print(FLAGS)
        self.recv_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.file_name = None
        self.file_size = None
        self.file_recv_cur_size = 0
        self.ip = None
        self.port = None
        self.sender_wind_size = 1

        self.timeout_count = 7
        self.file_name = files



    def checksum(self,data):
        hashing = hashlib.sha1()
        hashing.update(data)
        return hashing.digest()



    def unpack_data(self,data):
        return_value = dict()
        type_i = chr(data[0])
        recv_checksum = None
        if type_i == 'i':
            file_size = int.from_bytes(data[1:21], byteorder="big")
            file_name = data[21:41].decode("utf-8").rstrip()
            recv_checksum = struct.unpack("20s",data[41:61])[0]
            payload = data[61:]
            check_checksum = self.checksum(chr(data[0]).encode() + data[1:21] +data[21:41]+ payload)
            #print (type_i, file_size, file_name, recv_checksum, payload, check_checksum)

            return (type_i, file_size, file_name, recv_checksum, payload, check_checksum)

        elif type_i == 'd':
            current_length = int.from_bytes(data[1:21],byteorder="big")
            seq_num = int.from_bytes(data[21:41], byteorder="big")
            recv_checksum = struct.unpack("20s",data[41:61])[0]
            payload = data[61:]

            check_checksum = self.checksum(chr(data[0]).encode() + data[1:21] +data[21:41]+ payload)

            return (type_i, current_length, seq_num, recv_checksum, payload, check_checksum)





    def send(self,data):
        self.recv_socket.sendto(data,(self.ip, self.port))

    def recv(self):
        return self.recv_socket.recvfrom(1500)

    def timeout_occur(self):
        if self.timeout_count == 0 :
            print("COUNT:",self.timeout_count)
            print(self.timeout_count)
            time.sleep(7)
            self.timeout_count = 7




    def recv_go_back_N(self):
        self.recv_socket.bind(('',8000))
        data, addr = self.recv_socket.recvfrom(1500)
        self.ip = addr[0]
        self.port = addr[1]
        start_time = time.time()

        result = self.unpack_data(data)

        if result[3] == result[5]:
            if result[0] == 'i':
                #print("write")
                self.file_size = result[1]
                #print(self.file_size)
                #self.file_name = result[2]
                payload = result[4]
                self.file_recv_cur_size += len(payload)
                self.send('ACK'.encode())

        with open(self.file_name,'wb') as recv_file:
            recv_file.write(payload)
            print("current_size/totalsize = {0} / {1} , {2} %".\
            format(self.file_recv_cur_size,self.file_size,\
            int(self.file_recv_cur_size/self.file_size*100)))

            while self.file_recv_cur_size < self.file_size:

                try:
                    data, addr = self.recv_socket.recvfrom(1500)
                    result = self.unpack_data(data)

                    if result[3] == result[5]:
                        if result[0] == 'd':
                            seq_num = result[2]
                            self.file_recv_cur_size += result[1]
                            payload = result[4]
                            recv_file.write(payload)

                            send_num = self.check_next_seq_num(seq_num)
                            ack_msg = 'ACK {}'.format(str(send_num))

                            self.send(ack_msg.encode())


                    print("current_size / totalsize = {0} / {1} , {2} %".\
                    format(self.file_recv_cur_size,self.file_size,\
                           self.file_recv_cur_size/self.file_size*100))
                    self.timeout_count -= 1

                except socket.timeout:
                    print("TIME OUT Occur")

        end_time = time.time()
        print("SEND COMPLETE : ",   end_time - start_time)

    def check_next_seq_num(self, seq_num):
        send_num = 0
        if seq_num == 0 :
            send_num = 1
        elif seq_num == 1:
            send_num = 0
        return send_num

    def write_start(self,file_name,data):
        file_name = str("recv_"+file_name)

        with open(file_name,'wb') as recv_file:
            recv_file.write(data)
            print("write complete")



    def main(self):
        self.recv_go_back_N()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', type=str,
                         default='localhost')
    parser.add_argument('-p', '--port', type=int,
                         default=8000)
    parser.add_argument('-f', '--files', type=str)

    FLAGS = parser.parse_known_args()
    args = parser.parse_args()

    send = receiver(FLAGS,args.files)
    send.main()
