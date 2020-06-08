#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('-I. --all trawlnet.ice') 
import TrawlNet

class ReceiverI(TrawlNet.Receiver):
    def start():
        pass

    def destroy():
        pass

class ReceiverFactoryI(TrawlNet.ReceiverFactory):
    def create(self, fileName, sender, transfer ,current = None):
        print("Receiver Factory"+ fileName)
        servant = ReceiverI()
        proxy = current.adapter.addWithUUID(servant)
        return TrawlNet.ReceiverPrx.checkedCast(proxy)


class Client(Ice.Application):
    def run(self, argv):
        proxyTransfer = self.communicator().stringToProxy(argv[1])
        transferFactory = TrawlNet.TransferFactoryPrx.checkedCast(proxyTransfer)

        if not transferFactory:
            raise RuntimeError('Invalid proxy transferFactory')

        receiverFactory = ReceiverFactoryI()
        transferFactory.newTransfer(receiverFactory)
        
        return 0
        
sys.exit(Client().main(sys.argv))