#!/usr/bin/env python3

# FlutterPi.py - A simple IRC-bot written in python
#
# Copyright (C) 2015 : Niklas Hempel - http://liq-urt.de
# Modifications Copyright (C) 2019 Jacob Harris - https://github.com/Flutterdashie/
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
from unidecode import unidecode
import re
import socket

# --------------------------------------------- Start Settings ----------------------------------------------------
HOST = "irc.twitch.tv"                          # Hostname of the IRC-Server in this case twitch's
PORT = 6667                                     # Default IRC-Port
with open('privatedata.txt','r') as f:          # Using this to prevent exposing my OAuth
    CHAN = f.readline().strip('\n')             # And this to prevent channel changes causing updates to this file
    NICK = f.readline().strip('\n')             # And this just because file completion.
    PASS = f.readline().strip('\n')             # www.twitchapps.com/tmi/ will help to retrieve the required authkey
# --------------------------------------------- End Settings -------------------------------------------------------


# --------------------------------------------- Start Functions ----------------------------------------------------
def send_pong(msg):
    con.send(bytes('PONG %s\r\n' % msg, 'UTF-8'))


def send_message(chan, msg):
    con.send(bytes('PRIVMSG %s :%s\r\n' % (chan, msg), 'UTF-8'))


def send_nick(nick):
    con.send(bytes('NICK %s\r\n' % nick, 'UTF-8'))


def send_pass(password):
    con.send(bytes('PASS %s\r\n' % password, 'UTF-8'))


def join_channel(chan):
    con.send(bytes('JOIN %s\r\n' % chan, 'UTF-8'))


def part_channel(chan):
    con.send(bytes('PART %s\r\n' % chan, 'UTF-8'))
# --------------------------------------------- End Functions ------------------------------------------------------


# --------------------------------------------- Start Helper Functions ---------------------------------------------
def get_sender(msg):
    result = ""
    for char in msg:
        if char == "!":
            break
        if char != ":":
            result += char
    return result


def get_message(msg):
    result = ""
    i = 4
    length = len(msg)
    while i < length:
        result += msg[i] + " "
        i += 1
    result = result.lstrip(':')
    return result


def get_userdata(data):
    r = re.compile(";([^;]*)=1;")
    result = re.findall(r,data)
    #print(result)
    return result

def get_cheer_amount(data):
    for item in data.split(';'):
        result = re.match(r"bits=(\d+)",item)
        if not(result is None):
            print("I DID IT")
            print("REDDIT")
            return int(result.group(1))
    else:
        print("no bitties here")
        return 0

def clean_userdata(data):
    if(len(data) == 0):
        return ""
    else:
        return ' '.join(data) + ' '

def parse_message(msg):
    if len(msg) >= 1:
        msg = msg.split(' ')
        options = {'!test': command_test,
                   '!asdf': command_asdf}
        if msg[0] in options:
            options[msg[0]]()
# --------------------------------------------- End Helper Functions -----------------------------------------------


# --------------------------------------------- Start Command Functions --------------------------------------------
def command_test():
    print("no u")


def command_asdf():
    print("who said that")

def send_def(msg):
    send_message(CHAN,msg)
    
# --------------------------------------------- End Command Functions ----------------------------------------------
print('Connecting to {0} as {1}...'.format(CHAN,NICK))
con = socket.socket()
con.connect((HOST, PORT))
con.send(bytes('CAP REQ :twitch.tv/membership twitch.tv/tags twitch.tv/commands\r\n','utf-8'))
send_pass(PASS)
send_nick(NICK)
join_channel(CHAN)
#CHEERMOTE = re.compile(r"\w{4,}?\d+")
data = ""

while True:
    try:
        data = data+con.recv(1024).decode('UTF-8')
        data_split = re.split(r"[~\r\n]+", data)
        data = data_split.pop()

        for line in data_split:
            line = str.rstrip(line)
            line = str.split(line)

            if len(line) >= 1:
                if line[0] == 'PING':
                    send_pong(line[1])

                elif line[2] == 'PRIVMSG':
                    userdata = get_userdata(line[0])
                    bits = get_cheer_amount(line[0])
                    sender = get_sender(line[1])
                    message = get_message(line)
                    parse_message(message)

                    if bits != 0:
                        print("holy crap somebody cheered" + bits + " bits!")
                    print(clean_userdata(userdata) + sender + ": " + unidecode(message))
                elif line[2] == 'WHISPER':
                    sender = get_sender(line[1])
                    message = get_message(line)
                    parse_message(message)

                    print(sender + " whispered: " + unidecode(message))

                

    except socket.error:
        print("Socket died")

    except socket.timeout:
        print("Socket timeout")

#@badge-info=subscriber/21;badges=subscriber/18;bits=100;color=#988634;display-name=DCraftiest;emotes=;flags=;id=601c95bc-54ee-4cdd-89d1-d76ff8e18b86;mod=0;room-id=21836069;subscriber=1;tmi-sent-ts=1555991744580;turbo=0;user-id=62964483;user-type=
