#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('-I. --all trawlnet.ice') 
import TrawlNet


class TransferI(TrawlNet.Transfer):
    def createPeers(files):
        pass    
    def destroyPeer(peerId):
        pass
    
    def destroy():
        print("Hola")
        sys.stdout.flush()

class TransferFactoryI(TrawlNet.TransferFactory):
    def newTransfer(self, receiverFactory, current = None):
        print("Papi")
        servant = TransferI()
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
        servant = TransferFactoryI()

        adapter = broker.createObjectAdapter("TransferFactoryAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("transferFactory1"))

        print(proxy, flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))