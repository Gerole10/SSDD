#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('-I. --all trawlnet.ice') 
import TrawlNet


class TransferI(TrawlNet.Transfer):
    def __init__(self, receiverFactory, senderFactory):
        self.receiverFactory = receiverFactory
        self.senderFactory = senderFactory

    def createPeers(self, files):
        pass    

    def destroyPeer(self, peerId):
        pass
    
    def destroy(self):
        pass

class TransferFactoryI(TrawlNet.TransferFactory):
    def __init__(self, senderFactory):
        self.senderFactory = senderFactory

    def newTransfer(self, receiverFactory, current = None):
        servant = TransferI(receiverFactory, self.senderFactory)
        proxy = current.adapter.addWithUUID(servant)
        return TrawlNet.TransferPrx.checkedCast(proxy)

class Server(Ice.Application):
    def run(self, argv):
        #Conexion con sender_factory
        proxySender = self.communicator().stringToProxy(argv[1])
        senderFactory = TrawlNet.SenderFactoryPrx.checkedCast(proxySender)

        if not senderFactory:
            raise RuntimeError('Invalid proxy for senderFactory')

        senderFactory.create("nombreArchivo")

        #Configuracion del proxy
        broker = self.communicator()
        servant = TransferFactoryI(senderFactory)

        adapter = broker.createObjectAdapter("TransferFactoryAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("transferFactory1"))

        print(proxy, flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))