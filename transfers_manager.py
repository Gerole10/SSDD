#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('-I. --all trawlnet.ice') 
import TrawlNet


class TransferI(TrawlNet.Transfer):
    def __init__(self, receiverFactory, senderFactory, transfer = None):
        self.receiverFactory = receiverFactory
        self.senderFactory = senderFactory
        self.transfer = transfer
        self.receiverList = []

    def createPeers(self, files, current = None):
        for file in files:
            print("Creacion peer archivo "+file)
            try:
                sender = self.senderFactory.create(file)
                receiver = self.receiverFactory.create(file, sender, self.transfer)
                self.receiverList.append(receiver)
            except FileNotFoundError as err:
                print(err.args)
        return self.receiverList

    def destroyPeer(self, peerId, current = None):
        print("Destruyendo peer del archivo:"+peerId)
        for receiver in self.receiverList:
            print(receiver)
            receiver.fileName
            #Quiza falte poner el adaptador del receive activo
            #if receiver.fileName == peerId:
             #   print("HAy un igual: "+peerId+" y "+receiver.fileName)
            #receiver.destroy()
            
    def destroy(self):
        pass

class TransferFactoryI(TrawlNet.TransferFactory):
    def __init__(self, senderFactory):
        self.senderFactory = senderFactory

    def newTransfer(self, receiverFactory, current = None):
        servant = TransferI(receiverFactory, self.senderFactory)
        proxy = current.adapter.addWithUUID(servant)
        transferPrx = TrawlNet.TransferPrx.checkedCast(proxy)
        servant.transfer = transferPrx

        return transferPrx

class Server(Ice.Application):
    def run(self, argv):
        #Conexion con sender_factory
        proxySender = self.communicator().stringToProxy(argv[1])
        senderFactory = TrawlNet.SenderFactoryPrx.checkedCast(proxySender)

        if not senderFactory:
            raise RuntimeError('Invalid proxy for senderFactory')

        #senderFactory.create("nombreArchivo")

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