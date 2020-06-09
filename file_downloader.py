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
    def __init__(self):
        print("Constructor receiverFactory")

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

        
        broker = self.communicator()
        servant = ReceiverFactoryI()

        adapter = broker.createObjectAdapter("ReceiverFactoryAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("receiverFactory1"))
        print(proxy)
        transfer = transferFactory.newTransfer(TrawlNet.ReceiverFactoryPrx.checkedCast(proxy))
        print(transfer)    
        adapter.activate()

        files = Client.crearListaFiles(argv)
        #transfer.createPeers(files)


        return 0

    def crearListaFiles(argv):
        files = []
        if len(argv) > 2:
            for i in range(2, len(argv)):
                files.append(argv[i])
                print(argv[i])
        else:
            print("Introduzca los archivos por parametros")
        print(files)
        return files
        
sys.exit(Client().main(sys.argv))