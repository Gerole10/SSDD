#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('-I. --all trawlnet.ice') 
import TrawlNet


class TransferI(TrawlNet.Transfer):

    def destroy():
        print("Hola")
        sys.stdout.flush()


class Server(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        servant = TransferI()

        adapter = broker.createObjectAdapter("Transfer1Adapter")
        proxy = adapter.add(servant, broker.stringToIdentity("transfer1"))

        print(proxy, flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))