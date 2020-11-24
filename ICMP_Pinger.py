# ICMP_Pinger Lab
# By: Kyle Duncan, Joseph Bulanon, and Dustin Hatlen
# Sources used in this project:
#   
#   IP Addresses:
#       => https://www.dotcom-monitor.com/blog/technical-tools/network-location-ip-addresses/
#   
#   ICMP Error Codes  
#       => https://www.erg.abdn.ac.uk/users/gorry/course/inet-pages/icmp-code.html#:~:text=Many%20of%20the%20types%20of,%2C%20Time%20Exceeded%20(11).&text=Many%20of%20these%20ICMP%20types%20have%20a%20%22code%22%20field.
#       => http://en.wikipedia.org/wiki/Internet_Control_Message_Protocol#Control_messages

from socket import *
import os
import sys
import struct
import time
import select
import binascii
from termcolor import colored
from icmp_errors import ICMP_CONTROL_MESSAGE

ICMP_ECHO_REQUEST = 8

def avgPingTime(arr):
    sum = 0
    
    for element in arr:
        sum += element
    
    return sum / len(arr)
      

def checksum(string): 
    csum = 0
    countTo = (len(string) // 2) * 2  
    count = 0

    while count < countTo:
        thisVal = string[count+1] * 256 + string[count] 
        csum = csum + thisVal
        csum = csum & 0xffffffff  
        count = count + 2
    
    if countTo < len(string):
        csum = csum + string[len(string) - 1]
        csum = csum & 0xffffffff 
    
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum 
    answer = answer & 0xffff 
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    
    while 1: 
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        timeReceived = time.time() 

        if whatReady[0] == []: # Timeout
            return None, True, {'type': 3, 'code': 0}

        recPacket, addr = mySocket.recvfrom(1024)

        # accessing icmp header from the receieved packet
        icmpHeader = recPacket[20:28]
        icmpType, code, checksum, replyID, sequence = struct.unpack("bbHHh", icmpHeader)
        
        icmp_header = {
            'type': icmpType,
            'code': code,
            'checksum': checksum,
            'id': replyID,
            'sequence': sequence
        }

        
        # the icmp code and type must both be 0 in the ICMP reply
        if code == 0 and icmpType == 0:
            # verify the ID of packet
            if replyID == ID:
                bytesInDouble = struct.calcsize("d")
                timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
                return timeReceived - timeSent, False, icmp_header
        
        timeLeft = timeLeft - howLongInSelect

        if timeLeft <= 0:
            return None, True, icmp_header


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    
    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)
    
    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xffff        
    else:
        myChecksum = htons(myChecksum)
        
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    
    mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.


def doOnePing(destAddr, timeout): 
    icmp = getprotobyname("icmp")
    # SOCK_RAW is a powerful socket type. For more details:   http://sock-raw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay, error_flag, icmp_header = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()

    icmp_type = icmp_header["type"]
    icmp_code = icmp_header["code"]

    if delay:
        return delay, error_flag
    else:
        icmp_message = ICMP_CONTROL_MESSAGE[icmp_type][icmp_code]
        delay = f'{icmp_code}: {icmp_message}' # return the error code and message

    return delay, error_flag


def ping(location, host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    dest = gethostbyname(host)
    print(colored("Pinging", 'yellow'), colored(location, 'green'), colored("using Python:", 'yellow'))
    print("")
    
    # Send ping requests to a server separated by approximately one second
    count = 0
    ping_times = [] # initialize empty array for keeping track of the ping times to the server

    while count < 10:
        print(colored(f'Ping {count + 1}:', 'cyan'))
        delay, error_flag = doOnePing(dest, timeout) # ping the server
        
        if error_flag: # if the ping timed out or resulted in an error don't add it to the list of pings
            print(colored('Error', 'red'), delay)
        else:
            if delay != '0: Echo Reply': # only receieves 'Echo Reply' when pinging local host time is less than 1 ms 
                delay *= 1000 # convert delay into milliseconds
                print(f'{delay} ms')
                ping_times.append(delay) # the ping did not time out so append it to the list
            else:
                delay = 0.0
                print(f'{delay} ms')
                ping_times.append(delay) # the ping did not time out so append it to the list
        count += 1
        time.sleep(1) # wait one second
    return ping_times


def pingReport(pings):
    # if at least one ping did not timeout calculate the average ping time, and the min and max ping times
    if len(pings) != 0:
        min_ping = min(pings)
        max_ping = max(pings)
        avg_ping = avgPingTime(pings)

        print('\n')
        print(colored('Maxmimum Ping Time:', 'cyan'), f'{max_ping} ms')
        print(colored('Minimum Ping Time:', 'cyan'), f'{min_ping} ms')
        print(colored('Average Ping Time:', 'cyan'), f'{avg_ping} ms')


def pingServers():
    # create an array of server objects => obtained IP addresses from https://www.dotcom-monitor.com/blog/technical-tools/network-location-ip-addresses/
    # in this case ping servers from 6 of the 7 contients

    servers = [
        {'location': 'North America', 'address': '207.228.238.7'}, 
        {'location': 'South America', 'address': '131.255.7.26'},
        {'location': 'Europe', 'address': '51.158.22.211'} , 
        {'location': 'Australia', 'address': '101.0.86.43'},
        {'location': 'Asia', 'address': '47.94.129.116'},
        {'location': 'Africa', 'address': '197.221.23.194'}
    ]

    # ping every server 10 times
    for server in servers:
        continent = server['location']
        address = server['address']
        ping_times = ping(location=continent, host=address)
        
        pingReport(pings=ping_times)
        
        print(colored('Packet Loss:', 'cyan'), f'{((10 - len(ping_times)) / 10) * 100}%')
        print('\n', '-------------------------------------------------', '\n')


# entry point for the program
if __name__ == "__main__":
    '''# start by pinging localhost
    print('\n', '-------------------------------------------------', '\n')
    ping_times = ping('self', '127.0.0.1')
    pingReport(pings=ping_times)
    print(colored('Packet Loss:', 'cyan'), f'{((10 - len(ping_times)) / 10) * 100}%')
    # ping servers from 6 of the 7 contients'''
    print('\n', '-------------------------------------------------', '\n')
    pingServers()