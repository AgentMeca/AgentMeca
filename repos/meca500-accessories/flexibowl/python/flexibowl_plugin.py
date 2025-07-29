"""
FlexiBowl Plugin for Industrial Automation

This module provides functions to communicate with FlexiBowl devices via TCP/IP.
FlexiBowl is a flexible parts feeding system used in industrial automation.

Functions:
    in_allarm(ip): Check if the FlexiBowl device is in alarm state
    move_flb1(ip, command): Send movement commands to the FlexiBowl device
"""

import socket
from time import sleep
import sys


def in_allarm(ip):
    """
    Check if the FlexiBowl device is in alarm state.
    
    Args:
        ip (str): IP address of the FlexiBowl device
        
    Returns:
        bool: True if device is operational (no alarms), False if in alarm state or connection failed
    """
    assert type(ip) is str
    TCP_IP = ip
    TCP_PORT = 7776
    BUFFER_SIZE = 1024
    command = "AL"
    # Create alarm check message: NULL + 7 + "AL" + CR
    MESSAGE = chr(0)+chr(7)+command+chr(13)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((TCP_IP, TCP_PORT))
        s.send(MESSAGE.encode())
        data = s.recv(BUFFER_SIZE)
        print("Message send: " + MESSAGE)
        print("Message recive: " + str(data))
        sleep(0.1)  # Brief delay for message processing
    except :
        print("Not Connected1")
        s.close()
        return False
    # Extract alarm status from response (bytes 5 onwards contain hex alarm data)
    my_hexdata = data[5:None]
    print(my_hexdata)
    
    # Convert hex alarm data to binary for bit analysis
    scale = 16  # Hexadecimal base
    num_of_bits = 16
    binary_string = bin(int(my_hexdata, scale))[2:].zfill(num_of_bits)
    print(binary_string)
    
    # Convert binary to decimal to check for any alarm bits set
    error_decimal = int(binary_string, 2)
    if(error_decimal > 0):
        # Device is in alarm state
        s.close()
        return False
    else:
        s.close()
        return True

def move_flb1(ip, command):
    """
    Send movement commands to the FlexiBowl device.
    
    Args:
        ip (str): IP address of the FlexiBowl device
        command (str): Command to execute. Valid commands:
            - "MOVE": Basic movement
            - "MOVE FLIP": Move with flip action
            - "MOVE BLOW FLIP": Move with blow and flip
            - "MOVE BLOW": Move with blow action
            - "SHAKE": Shake the bowl
            - "LIGHT ON": Turn on illumination
            - "LIGHT OFF": Turn off illumination
            - "FLIP": Flip action only
            - "BLOW": Blow action only
            - "QUICK EMPTY OPTION": Quick empty sequence
            
    Returns:
        bool: True if command executed successfully, False otherwise
    """
    assert type(command) is str
    assert type(ip) is str
    TCP_IP = ip
    TCP_PORT = 7776
    BUFFER_SIZE = 1024

    # Map human-readable commands to FlexiBowl protocol commands
    if(command=="MOVE"):
        command="QX2"
    elif (command=="MOVE FLIP"):
        command="QX3"
    elif (command=="MOVE BLOW FLIP"):
        command="QX4"
    elif (command=="MOVE BLOW"):
        command="QX5"
    elif (command=="SHAKE"):
        command="QX6"
    elif (command=="LIGHT ON"):
        command="QX7"
    elif (command=="LIGHT OFF"):
        command="QX8"
    elif (command=="FLIP"):
        command="QX10"
    elif (command=="BLOW"):
        command="QX9"
    elif (command=="QUICK EMPTY OPTION"):
        command="QX11"
    else:
        command="QX60"  # Invalid command - will cause device to reject
    # Create command message: NULL + 7 + command + CR
    MESSAGE = chr(0)+chr(7)+command+chr(13)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((TCP_IP, TCP_PORT))
        s.send(MESSAGE.encode())
        data = s.recv(BUFFER_SIZE)
        print("Message send: " + MESSAGE)
        print("Message recive: " + str(data))
        sleep(0.1)  # Brief delay for message processing
        
        # Check if device responded with "%" indicating command acceptance
        if(b"%" in data):
            print("Command accepted, waiting for completion...")
            moving = 1
            # Wait for movement/operation to complete
            while True:

                # Different status checking methods for different command types
                if(command=="QX11") or (command=="QX10") or (command=="QX4") or (command=="QX3"):
                    # For these commands, check IO status (busy signal)
                    print("Checking device busy status...")
                    sleep(0.1)
                    MESSAGE = chr(0)+chr(7)+"IO"+chr(13)  # IO status query
                    s.send(MESSAGE.encode())
                    data = s.recv(BUFFER_SIZE)
                    print(data)
                    moving = data[12:-1]  # Extract busy status from response
                    print(moving)
                    if int(moving) == 1:  # Device reports not busy (operation complete)
                        sleep(0.1)
                        break
                else:
                    # For other commands, check SC (status/completion) register
                    MESSAGE = chr(0)+chr(7)+"SC"+chr(13)  # Status check query
                    s.send(MESSAGE.encode())
                    data = s.recv(BUFFER_SIZE)
                    moving = data[7:-2]  # Extract status from response
                    if int(moving) == 0:  # Operation completed
                        sleep(0.1)
                        break
                sleep(0.1)  # Polling interval for status checks
            s.close()
            return True
        else:
            s.close()
            return False
    except :
        print("Not Connected2")
        s.close()
        return False