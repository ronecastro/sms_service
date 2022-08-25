import serial
import subprocess
import threading

BUFFER=320

def write_to_ser(ser, proc):
      while True:
          ser.write(proc.stdout.read(BUFFER))

def read_from_ser(ser, proc):
      while True:
          play.stdin.write(ser.read(BUFFER))

threads = []
with serial.Serial('/dev/ttyUSB0', 230400, timeout=1, dsrdtr=True, rtscts=True) as ser:
  ffmpeg = subprocess.Popen('ffmpeg -re -f pulse -i default -f s16le -c:a pcm_s16le -ar 4000 -'.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  play = subprocess.Popen('play -r 8000 -t s16 -'.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  t1 = threading.Thread(target=write_to_ser, args=(ser, ffmpeg))
  t2 = threading.Thread(target=read_from_ser, args=(ser, play))
  t1.start()
  t2.start()
  t1.join()
  t2.join()
ser.close()