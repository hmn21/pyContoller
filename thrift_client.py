#!/usr/bin/python2.7

# -*- coding: UTF-8 -*-
from __future__ import print_function
import traceback
import os, sys
# sys.path.append("python_package/xlrd/lib/python")
# sys.path.append("python_package/xlwt/lib")

import ctypes
# for thrift

import sys, glob

# auto-generated library
sys.path.append('gen-py')
sys.path.insert(0, glob.glob('lib/py/build/lib*')[0])

from nautilus.ControlService import ControlService
from nautilus.ControlService import MonitorService

from nautilus.ControlService.ttypes import *

from nautilus.common.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


# for thread
import thread
import time
import threading
# for log
from  log_config import *

if os.name == 'nt':
    import msvcrt

# Posix (Linux, OS X)
else:
    import sys
    import termios
    import atexit
    from select import select

class KBHit:
    
    def __init__(self):
        '''Creates a KBHit object that you can call to do various keyboard things.
        '''

        if os.name == 'nt':
            pass
        
        else:
    
            # Save the terminal settings
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)
    
            # New terminal setting unbuffered
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)
    
            # Support normal-terminal reset at exit
            atexit.register(self.set_normal_term)
    
    
    def set_normal_term(self):
        ''' Resets to normal terminal.  On Windows this is a no-op.
        '''
        
        if os.name == 'nt':
            pass
        
        else:
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)


    def getch(self):
        ''' Returns a keyboard character after kbhit() has been called.
            Should not be called in the same program as getarrow().
        '''
        
        s = ''
        
        if os.name == 'nt':
            return msvcrt.getch().decode('utf-8')
        
        else:
            return sys.stdin.read(1)
                        

    def getarrow(self):
        ''' Returns an arrow-key code after kbhit() has been called. Codes are
        0 : up
        1 : right
        2 : down
        3 : left
        Should not be called in the same program as getch().
        '''
        
        if os.name == 'nt':
            msvcrt.getch() # skip 0xE0
            c = msvcrt.getch()
            vals = [72, 77, 80, 75]
            
        else:
            c = sys.stdin.read(3)[2]
            vals = [65, 67, 66, 68]
        
        return vals.index(ord(c.decode('utf-8')))
        

    def kbhit(self):
        ''' Returns True if keyboard character was hit, False otherwise.
        '''
        if os.name == 'nt':
            return msvcrt.kbhit()
        
        else:
            dr,dw,de = select([sys.stdin], [], [], 0)
            return dr != []


class TestThriftServer:
    #def __init__(self, ip_add, port, md_gui):
    def __init__(self, ip_add, port):
        self.ip = ip_add
        self.port = port

        self.client = self.CreateClient()

    def CreateClient(self):
     # Make socket
        transport = TSocket.TSocket(self.ip, self.port)

        # Buffering is critical. Raw sockets are very slow
        transport = TTransport.TBufferedTransport(transport)

        # Wrap in a protocol
        protocol = TBinaryProtocol.TBinaryProtocol(transport)

        client = ControlService.Client(protocol)

        # Connect!
        transport.open()
        # Close!
        # transport.close()

        # Create a client to use the protocol encoder
        return client

    def Ping(self):
        try:
            ret_error = self.client.Ping("python")
            log.info('Ping(), return:{}'.format(ret_error))
        except Thrift.TException as tx:
            log.info(('Get Exception Ping()%s' % (tx.message)))


    def QryThread(self):
        while 1:
            try:
                ret_error = self.client.Ping("python win")
                log.info('Ping(), return:{}'.format(ret_error))

                request = nautilus.common.ttypes.Request()
                request.result = 100
                request.guestName = "test from py"

                ret_QryParams = self.client.PullMsg(request);
                log.info('QryDefaultParams(), return:{}'.format(ret_QryParams.count))

            except Thrift.TException as tx:
                log.info(('Get Exception ()%s' % (tx.message)))

            time.sleep(2)


    def Start(self):
        # Create two threads as follows
        try:
            thread.start_new_thread( self.QryThread, () )
        except:
            log.info ("Error: unable to start thread")

class Feed:
    def __init__(self, ip_add, port):
        self.ip = ip_add
        self.port = port
        self.client = self.CreateClient()
        #self.PullFeeds()


    def CreateClient(self):
     # Make socket
        transport = TSocket.TSocket(self.ip, self.port)

        # Buffering is critical. Raw sockets are very slow
        transport = TTransport.TBufferedTransport(transport)

        # Wrap in a protocol
        protocol = TBinaryProtocol.TBinaryProtocol(transport)

        client = ControlService.Client(protocol)

        # Connect!
        transport.open()
        return client

    def Ping(self):
        try:
            ret_error = self.client.Ping("python")
            log.info('Ping(), return:{}'.format(ret_error))
        except Thrift.TException as tx:
            log.info(('Get Exception Ping()%s' % (tx.message)))

    def Init(self, sett):
        try:
            settings = nautilus.common.ttypes.Settings()
            settings.fields = []
            settings.count = 0
            for i in sett:
                param = nautilus.common.ttypes.Param()
                name, value = i
                param.name = name
                param.val = value
                settings.fields.append(param)
                settings.count += 1

            ret_error = self.client.Init(settings)
            log.info('Init(), return:{}'.format(ret_error))
        except Thrift.TException as tx:
            log.info(('Get Exception Init()%s' % (tx.message)))


    def ChangeStratStatus(self, stratID, status):
        try:
            Status = nautilus.common.ttypes.Status()
            Status.status = status
            Status.stratID = stratID
            ret_error = self.client.ChangeStratStatus(Status)
            log.info('ChangeStratStatus(), return:{}'.format(ret_error))
        except Thrift.TException as tx:
            log.info(('Get Exception ChangeStratStatus()%s' % (tx.message)))


    def PullFeeds(self):
        while 1:
            try:
                request = nautilus.common.ttypes.Request()
                request.result = 1
                request.guestName = "thrift_client"
                rtn_feeds = self.client.PullFeeds(request)
                log.info('PullFeeds(), return:{}'.format(rtn_feeds.count))
                for feed in rtn_feeds.feeds:
                    print('PullFeeds(), return: ', feed.Type, feed.instrumentID, feed.lastTradePrice)

            except Thrift.TException as tx:
                log.info(('Get Exception PullFeeds()%s' % (tx.message)))

            time.sleep(1)

    def PullMsg(self):
        try:
            request = nautilus.common.ttypes.Request()
            request.result = 1
            request.guestName = "thrift_client"
            ret_QryParams = self.client.PullMsg(request)
            if ret_QryParams.count != 0:
                log.info('PullMsg(), return:{}'.format(ret_QryParams.count))
            for i in ret_QryParams.notifications:
            	print(i.stratID, i.msgType, i.msg)

        except Thrift.TException as tx:
            log.info(('Get Exception PullMsg()%s' % (tx.message)))

class Monitor:
    def __init__(self, ip_add, port):
        self.ip = ip_add
        self.port = port
        self.client = self.CreateClient()
        #self.PullFeeds()

    def CreateClient(self):
     # Make socket
        transport = TSocket.TSocket(self.ip, self.port)

        # Buffering is critical. Raw sockets are very slow
        transport = TTransport.TBufferedTransport(transport)

        # Wrap in a protocol
        protocol = TBinaryProtocol.TBinaryProtocol(transport)

        client = MonitorService.Client(protocol)

        # Connect!
        transport.open()
        return client

    def Ping(self):
        try:
            ret_error = self.client.Ping("python")
            log.info('Ping(), return:{}'.format(ret_error))
        except Thrift.TException as tx:
            log.info(('Get Exception Ping()%s' % (tx.message)))

    def PullOrders(self):

        try:
            request = nautilus.common.ttypes.Request()
            request.result = 1
            request.guestName = "thrift_client"
            rtn_orders = self.client.PullOrders(request)
            if rtn_orders.count != 0:
                log.info('PullOrders(), return:{}'.format(rtn_orders.count))
            for order in rtn_orders.orders:
                print('PullOrders(), return: ', order.stratID, order.clientOrderID, order.instrumentID, order.dire, order.orderPrice, order.size, order.status, order.insertTime, order.updateTime)

        except Thrift.TException as tx:
            log.info(('Get Exception PullOrders()%s' % (tx.message)))


    def PullTrades(self):

        try:
            request = nautilus.common.ttypes.Request()
            request.result = 1
            request.guestName = "thrift_client"
            rtn_trades = self.client.PullTrades(request)
            if rtn_trades.count != 0:
                log.info('PullTrades(), return:{}'.format(rtn_trades.count))
            for trade in rtn_trades.trades:
                print('PullTrades(), return: ', trade.stratID, trade.clientOrderID, trade.instrumentID, trade.dire, trade.tradePrice, trade.tradeVol, trade.tradeTime)

        except Thrift.TException as tx:
            log.info(('Get Exception PullTrades()%s' % (tx.message)))



if __name__ == "__main__":
    try:
        #ip = raw_input("Please enter IP address: ")
        #port = input("Please enter controller port: ")


        """
        Configuration
        """
        ip = "172.30.50.112"
        controller_port = 40052
        monitor_port = 40051
        OctopusType_1 = "CTP"
        StratID = "123"
        StratType = "CommonPlec"
        OctopusType_2 = "CTP"
        MktType = "CTP"
        Instruments = "cu1605;cu1606"



        kb = KBHit()
        thrift_client = Feed(ip, controller_port)
        thrift_client.Ping()
        #port = input("Please enter monitor port: ")
        monitor_client = Monitor(ip, monitor_port)
        monitor_client.Ping()
        #OctopusType = raw_input("Please enter OctopusType: [CTP] ")
        thrift_client.Init([('StratType','MonitorStrategy'), ('OctopusType', OctopusType_1)])
                #StratID = raw_input("Please enter StratID: ")  
        #StratType = raw_input("Please enter StratType: [CommonPlec] ")
        #OctopusType_1 = raw_input("Please enter OctopusType: [CTP] ")
        #MktType = raw_input("Please enter MktType: [CTP] ")
        #Instruments = raw_input("Please enter Instruments: [cu1605;cu1606] ")
        thrift_client.Init([('StratID', StratID), ('StratType', StratType), ('OctopusType', OctopusType_2), ('MktType', MktType), ('Instruments', Instruments)])
        log.info("Monitor init success.")
        #StratStatus = input("Please change StratStatus: [1:run 2:stop 3:pause] ")
        StratStatus = 1
        thrift_client.ChangeStratStatus(StratID, StratStatus)
        print("Press any key to pause...")
        while 1:
            if kb.kbhit():
            	print("Pausing...")
                x = input("Please change StratStatus: [1:run 2:stop]")
                if x == 1:
                    print("Continue running...")
                elif x == 2:
                    print("Program stopping...")
                    thrift_client.ChangeStratStatus(StratID, 2)
                    sys.exit(0)
            else:
            	thrift_client.PullMsg()
            	monitor_client.PullTrades()
            	monitor_client.PullOrders()
            	time.sleep(0.5)


    except Exception:
        log.error("Got exception on TestThriftServer:%s", traceback.format_exc() )

