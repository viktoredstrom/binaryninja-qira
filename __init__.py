# -*- coding: utf-8 -*-
from binaryninja import *
from qirawebsocket import *
import threading
import time
import os

wsserver = None
msg_queue = []
bv = None

def plugin_start(asdf, function):
    global bv
    bv = asdf
    #sync_ninja_comments()
    threading.Thread(target=start_server).start()

def handle_message_queue():
    global msg_queue
    while len(msg_queue) > 0:
        dat = msg_queue[0].split(" ")
        msg_queue = msg_queue[1:]
        if dat[0] == "setaddress" and dat[1] != "undefined":
            try:
                a = int(str(dat[1][2:]),16)
                set_ninja_address(a)
            except e:
                print ("[QIRA Plugin] Error processing the address\n")

def start_server():
    global wsserver
    wsserver = SimpleWebSocketServer('', 3003, QiraServer)
    if wsserver is not None:
        wsserver.serveforever()

def ws_send(msg):
    global wsserver
    if (wsserver is not None) and (msg is not None):
        for conn in wsserver.connections.itervalues():
            conn.sendMessage(msg)

def set_ninja_address(addr):
    global bv
    bv.file.navigate(bv.file.view,addr)

def sync_ninja_comments(bv):
    for function in bv.functions:
        for addr, comment in function.comments.iteritems():
            ws_send("setcmt %s %s" % (hex(int(addr)), comment))

class QiraServer(WebSocket):
    def handleMessage(self):
        print self.data
        msg_queue.append(self.data)
        handle_message_queue()

PluginCommand.register_for_address("Qira-Ninja", "Since R2 is for madmen", plugin_start)
PluginCommand.register('Sync comments', 'Sync comments', sync_ninja_comments)
