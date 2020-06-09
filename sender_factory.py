#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('-I. --all trawlnet.ice') 
import TrawlNet


class SenderI(TrawlNet.Sender):
    def __init__(self, fileName):
        self.fileName = fileName

    def receive(size):
        pass

    def close():
        pass

    def destroy():
        print("Hola")
        sys.stdout.flush()

class SenderFactoryI(TrawlNet.SenderFactory):
    def create(self, fileName, current = None):
        print("Papi Sender"+ fileName)
        servant = SenderI(fileName)
        proxy = current.adapter.addWithUUID(servant)
        return TrawlNet.SenderPrx.checkedCast(proxy)

class Server(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        servant = SenderFactoryI()

        adapter = broker.createObjectAdapter("SenderFactoryAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("senderFactory1"))

        print(proxy, flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))