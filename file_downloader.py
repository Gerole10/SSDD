#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('-I. --all trawlnet.ice') 
import TrawlNet

class ReceiverI(TrawlNet.Receiver):
    def __init__(self, fileName, sender, transfer):
        self.fileName = fileName
        self.sender = sender
        self.transfer = transfer
    
    def start(self, current = None):
        print("Recevier del archivo: "+self.fileName)
        print(self.sender)
        print(self.transfer)

    def destroy():
        pass

class ReceiverFactoryI(TrawlNet.ReceiverFactory):
    def __init__(self):
        print("Constructor receiverFactory")

    def create(self, fileName, sender, transfer ,current = None):
        print("Creacion receiver "+ fileName)
        servant = ReceiverI(fileName, sender, transfer)
        proxy = current.adapter.addWithUUID(servant)
        return TrawlNet.ReceiverPrx.checkedCast(proxy)


class Client(Ice.Application):
    def run(self, argv):
        proxyTransfer = self.communicator().stringToProxy(argv[1])
        transferFactory = TrawlNet.TransferFactoryPrx.checkedCast(proxyTransfer)

        if not transferFactory:
            raise RuntimeError('Invalid proxy transferFactory')

        
        broker = self.communicator()
        servant = ReceiverFactoryI()

        adapter = broker.createObjectAdapter("ReceiverFactoryAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("receiverFactory1"))
        print(proxy)
        transfer = transferFactory.newTransfer(TrawlNet.ReceiverFactoryPrx.checkedCast(proxy))
        print(transfer)    
        adapter.activate()

        files = Client.createListFiles(argv)
        print(files)
        receiverList = transfer.createPeers(files)

        for receiver in receiverList:
            receiver.start()
        
        print(receiverList)
        return 0

    def createListFiles(argv):
        files = []
        if len(argv) > 2:
            for i in range(2, len(argv)):
                files.append(argv[i])
        else:
            print("Introduzca los archivos por parametros")
        return files
        
sys.exit(Client().main(sys.argv))