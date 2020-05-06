#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('-I. --all trawlnet.ice') 
import TrawlNet


class Client(Ice.Application):
    def run(self, argv):
        proxy = self.communicator().stringToProxy(argv[1])
        TransFactory = TrawlNet.TransferPrx.checkedCast(proxy)

        if not TransFactory:
            raise RuntimeError('Invalid proxy')

        #adapter = broker.createObjectAdapter("PrinterAdapter")
        #proxy = adapter.add(servant, broker.stringToIdentity("printer1"))

        TransFactory.destroy()

        return 0


class ReceiverFactoryI(TrawlNet.ReceiverFactory):
    def create(fileName, sender, transfer):


sys.exit(Client().main(sys.argv))