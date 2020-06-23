#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('-I. --all trawlnet.ice') 
import TrawlNet

class PeerEventI(TrawlNet.PeerEvent):
    def peerFinished(self, peerInfo, current = None):
        print("Notificando al transfer que el Peer ha finalizado")
        peerInfo.transfer.destroyPeer(peerInfo.fileName) 

class TransferI(TrawlNet.Transfer):
    def __init__(self, receiverFactory, senderFactory, transferEvent, transfer = None):
        self.receiverFactory = receiverFactory
        self.senderFactory = senderFactory
        self.transferEvent = transferEvent
        self.transfer = transfer
        self.peersDictionary = {}

    def createPeers(self, files, current = None):
        receiverList = []
        for fileName in files:
            print("Creacion peer archivo "+fileName)
            try:
                sender = self.senderFactory.create(fileName)
            except TrawlNet.FileDoesNotExistError as e:
                print(e.info)
                raise e
            else:
                receiver = self.receiverFactory.create(fileName, sender, self.transfer)
                receiverList.append(receiver)

                self.peersDictionary.setdefault(fileName,[receiver, sender])
                print("Imprimiendo diccionario")
                print(self.peersDictionary[fileName])

        return receiverList

    def destroyPeer(self, peerId, current = None):
        print("Destruyendo peer del archivo:"+peerId)
        receiver = self.peersDictionary[peerId][0]
        print(receiver)
        receiver.destroy()
        sender = self.peersDictionary[peerId][1]
        sender.destroy()

        self.peersDictionary.pop(peerId)
        print(len(self.peersDictionary))
        if len(self.peersDictionary) == 0:
            print("Diccionario vacio")
            self.transferEvent.transferFinished(self.transfer)
            
    def destroy(self, current):
        try:
            print("Destruido adaptador del transfer ")
            current.adapter.remove(current.id)
        except Exception as e:
            print(e)

class TransferFactoryI(TrawlNet.TransferFactory):
    def __init__(self, senderFactory, transferEvent):
        self.senderFactory = senderFactory
        self.transferEvent = transferEvent

    def newTransfer(self, receiverFactory, current = None):
        servant = TransferI(receiverFactory, self.senderFactory, self.transferEvent)
        proxy = current.adapter.addWithUUID(servant)
        transferPrx = TrawlNet.TransferPrx.checkedCast(proxy)
        servant.transfer = transferPrx

        return transferPrx

class Server(Ice.Application):
    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property {} not set".format(key))
            return None
        
        print("Using IceStorm in: '%s'"%key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def run(self, argv):
        #Conexion con sender_factory
        proxySender = self.communicator().stringToProxy("senderFactory1 -t -e 1.1 @ SenderFactory1")
        senderFactory = TrawlNet.SenderFactoryPrx.checkedCast(proxySender)

        if not senderFactory:
            raise RuntimeError('Invalid proxy for senderFactory')

        #Creacion topic PeerEvent Subscriber
        topic_mgr_peerEvent = self.get_topic_manager()
        if not topic_mgr_peerEvent:
            print ("Invalid proxy")
            return 2
        #Usar mismo adaptador!!
        ic_peerEvent = self.communicator()
        servant_peerEvent = PeerEventI()
        adapter_peerEvent = ic_peerEvent.createObjectAdapter("PeerEventAdapter")
        subscriber_peerEvent = adapter_peerEvent.addWithUUID(servant_peerEvent)

        topic_name_peerEvent = "PeerEventTopic"
        try:
            topic_peerEvent = topic_mgr_peerEvent.retrieve(topic_name_peerEvent)
        except IceStorm.NoSuchTopic:
            print("no such topic found, creating")
            topic_peerEvent = topic_mgr_peerEvent.create(topic_name_peerEvent)
        
        topic_peerEvent.subscribeAndGetPublisher({}, subscriber_peerEvent)

        #Creacion topic transferEvent Publisher
        topic_mgr_transferEvent = self.get_topic_manager()
        if not topic_mgr_transferEvent:
            print("Invalid proxy")
            return 2
        
        topic_name_transferEvent = "TransferEventTopic"
        try:
            topic_transferEvent = topic_mgr_transferEvent.retrieve(topic_name_transferEvent)
        except IceStorm.NoSuchTopic:
            print("no such topic found, creating")
            topic_transferEvent = topic_mgr_transferEvent.create(topic_name_transferEvent)
        
        publisher_transferEvent = topic_transferEvent.getPublisher()
        transferEvent = TrawlNet.TransferEventPrx.uncheckedCast(publisher_transferEvent)

        #Configuracion del proxy
        broker = self.communicator()
        servant = TransferFactoryI(senderFactory, transferEvent)

        adapter = broker.createObjectAdapter("TransferFactoryAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("transferFactory1"))

        print(proxy, flush=True)

        adapter_peerEvent.activate()
        adapter.activate()
        self.shutdownOnInterrupt()
        ic_peerEvent.waitForShutdown()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))