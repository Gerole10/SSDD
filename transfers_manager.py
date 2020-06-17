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
        self.dic = {}

    def createPeers(self, files, current = None):
        receiverList = []
        for file in files:
            print("Creacion peer archivo "+file)
            try:
                sender = self.senderFactory.create(file)
            except TrawlNet.FileDoesNotExistError as e:
                print(e.info)
                raise TrawlNet.FileDoesNotExistError(e.info)
            else:
                receiver = self.receiverFactory.create(file, sender, self.transfer)
                receiverList.append(receiver)

                self.dic.setdefault(file,[receiver, sender])
                print("Imprimiendo diccionario")
                print(self.dic[file])

        return receiverList

    def destroyPeer(self, peerId, current = None):
        print("Destruyendo peer del archivo:"+peerId)
        receiver = self.dic[peerId][0]
        print(receiver)
        receiver.destroy()
        sender = self.dic[peerId][1]
        sender.destroy()
        #diccionario.borrar[peerId]
        #if(diccionario=vacio){
        # transferEvent.transferFinished
        #}
            
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
        proxySender = self.communicator().stringToProxy("senderFactory1 -t -e 1.1 @ SenderFactory1")
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