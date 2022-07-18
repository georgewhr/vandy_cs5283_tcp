import socket
import utils
from utils import States
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# initial server_state
server_state = States.CLOSED

sock = socket.socket(socket.AF_INET,    # Internet
                     socket.SOCK_DGRAM) # UDP

sock.bind((UDP_IP, UDP_PORT)) # wait for connection

# Some helper functions to keep the code clean and tidy
def update_server_state(new_state):
  global server_state
  if utils.DEBUG:
    print(server_state, '->', new_state)
  server_state = new_state

# Receive a message and return header, body and addr
# addr is used to reply to the client
# this call is blocking
def recv_msg():
  data, addr = sock.recvfrom(1024)
  header = utils.bits_to_header(data)
  body = utils.get_body_from_data(data)
  print("in rece_msg")
  print(header)
  print(body)
  return (header, body, addr)

def is_solid_conn(ack, seq):
  if ack == seq:
    return True
  else:
    return False

# the server runs in an infinite loop and takes
# action based on current state and updates its state
# accordingly
# You will need to add more states, please update the possible
# states in utils.py file
while True:
  if server_state == States.CLOSED:
    # we already started listening, just update the state
    update_server_state(States.LISTEN)
  elif server_state == States.LISTEN:
    # we are waiting for a message
    header, body, addr = recv_msg()
    # if received message is a syn message, it's a connection
    # initiation
    if header.syn == 1:
      seq_number = utils.rand_int() # we randomly pick a sequence number
      ack_number = header.seq_num + 1
      # to be implemented
      
      print('connection startup:', addr)
      
      your_header_object = utils.Header(seq_number, ack_number, syn = 1, ack = 1)
      sock.sendto(your_header_object.bits(), addr)
      print('sent response with ack=', ack_number, 'seq=', seq_number)
      update_server_state(States.SYN_RECEIVED)

      ### sending message from the server:
      #   use the following method to send messages back to client
      #   addr is recieved when we receive a message from a client (see above)
      #   sock.sendto(your_header_object.bits(), addr)

  elif server_state == States.SYN_RECEIVED:
    header, body, addr = recv_msg()
    if header.ack == 1 and is_solid_conn(ack_number,header.seq_num ):
      update_server_state(States.CONNECTION_ESTALBSED)
      print("connection established")
  elif server_state == States.SYN_SENT:
    pass
  elif server_state == States.CONNECTION_ESTALBSED:
    header, body, addr = recv_msg()
    if header.fin == 1:
      print("Receiving FIN packet")
      ack_header_object = utils.Header(header.ack_num, header.seq_num + 1, ack = 1)
      sock.sendto(ack_header_object.bits(), addr)
      fin_header_object = utils.Header(header.ack_num, header.seq_num + 1, fin = 1)
      sock.sendto(fin_header_object.bits(), addr)
      server_state = States.CLOSE_WAIT
    elif header.ack == 1 and is_solid_conn(ack_number,header.seq_num ):
      print("receiving data:")
      print(body)
  elif server_state == States.CLOSE_WAIT:
    print("TCP session closed")
    header, body, addr = recv_msg()
    if header.ack == 1:
      print(header.seq_num)
      print(ack_number)
      server_state == States.CLOSED
  else:
    pass
  time.sleep(0.2)
