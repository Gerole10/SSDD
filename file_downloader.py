#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from io import open
import Ice
import IceStorm
Ice.loadSlice('-I. --all trawlnet.ice') 
import TrawlNet



class ReceiverI(TrawlNet.Receiver):
    def __init__(self, fileName, sender, transfer, peerEvent):
        self.fileName = fileName
        self.sender = sender
        self.transfer = transfer
        self.peerEvent = peerEvent
        self.puntero = 0

    def start(self, current = None):
        print("Recevier del archivo: "+self.fileName)
        print(self.sender)
        print(self.transfer)

        ar = open("./downloads/"+self.fileName,"w")
        print("Transfieriendo archivo "+self.fileName+" recibiéndose")
        while True:
            ar.seek(self.puntero)
            lectura = self.sender.receive(10)
            ar.write(lectura)
            self.puntero += 10
            if len(lectura) < 10:
                print("Transferencia de "+self.fileName+" completada.")
                self.sender.close()
                break
        #Aqui se emite el evento PeerFinished
        #Crear PeerInfo(Transfer, filename)
        print("Creando peerInfo")
        peerInfo = TrawlNet.PeerInfo()
        peerInfo.transfer = self.transfer
        peerInfo.fileName = self.fileName
        #Llamar a peerFinished
        print("Llamado metodo peerFinished")
        self.peerEvent.peerFinished(peerInfo)


    def destroy(self, current):
        try:
            print("Destruido adaptador del receiver "+self.fileName)
            current.adapter.remove(current.id)
        except Exception as e:
            print(e)


class ReceiverFactoryI(TrawlNet.ReceiverFactory):
    def __init__(self, peerEvent):
        print("Constructor receiverFactory")
        self.peerEvent = peerEvent

    def create(self, fileName, sender, transfer ,current = None):
        print("Creacion receiver "+ fileName)
        servant = ReceiverI(fileName, sender, transfer, self.peerEvent)
        proxy = current.adapter.addWithUUID(servant)
        return TrawlNet.ReceiverPrx.checkedCast(proxy)


class Client(Ice.Application):

    def get_topic_manager_peerEvent(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property {} not set".format(key))
            return None
        
        print("Using IceStorm in: '%s'"%key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def run(self, argv):

        #Conexion con transferFactory
        proxyTransfer = self.communicator().stringToProxy("transferFactory1 -t -e 1.1 @ TransferFactory1")
        transferFactory = TrawlNet.TransferFactoryPrx.checkedCast(proxyTransfer)

        if not transferFactory:
            raise RuntimeError('Invalid proxy transferFactory')

        #Creacion topic peerEvent Publisher
        topic_mgr_peerEvent = self.get_topic_manager_peerEvent()
        if not topic_mgr_peerEvent:
            print("Invalid proxy")
            return 2
        
        topic_name_peerEvent = "PeerEventTopic"
        try:
            topic_peerEvent = topic_mgr_peerEvent.retrieve(topic_name_peerEvent)
        except IceStorm.NoSuchTopic:
            print("no such topic found, creating")
            topic_peerEvent = topic_mgr_peerEvent.create(topic_name_peerEvent)
        
        publisher_peerEvent = topic_peerEvent.getPublisher()
        peerEvent = TrawlNet.PeerEventPrx.uncheckedCast(publisher_peerEvent)


        #Creacion proxy receiverFactory
        broker = self.communicator()
        servant = ReceiverFactoryI(peerEvent)

        adapter = broker.createObjectAdapter("ReceiverFactoryAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("receiverFactory1"))
        print(proxy)

        #Creacion transfer
        transfer = transferFactory.newTransfer(TrawlNet.ReceiverFactoryPrx.checkedCast(proxy))
        print(transfer)    
        adapter.activate()

        #Creacion lista archivos
        files = Client.createListFiles(argv)
        print(files)

        #Generacion de peers
        receiverList = []
        try:
            receiverList = transfer.createPeers(files)
        except TrawlNet.FileDoesNotExistError as e:
            print(e.info)
        #print(receiverList)

        for receiver in receiverList:
            receiver.start()
        
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