
import subprocess

p = subprocess.Popen(["python3", "stopAndWait_recv.py"])
while True:
    end = p.poll()
    if end is not None:
        print("end program!!")
        break
    continue

p = subprocess.Popen(["python3", 'recv_python_file.py'])
