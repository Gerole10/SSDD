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

        self.dic.pop(peerId)
        print(len(self.dic))
        if len(self.dic) == 0:
            print("Diccionario vacio")
            #transferEvent.transferFinished()
            
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
    def get_topic_manager_peerEvent(self):
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
        topic_mgr_peerEvent = self.get_topic_manager_peerEvent()
        if not topic_mgr_peerEvent:
            print ("Invalid proxy")
            return 2
        
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

        #Configuracion del proxy
        broker = self.communicator()
        servant = TransferFactoryI(senderFactory)

        adapter = broker.createObjectAdapter("TransferFactoryAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("transferFactory1"))

        print(proxy, flush=True)

        adapter_peerEvent.activate()
        adapter.activate()
        self.shutdownOnInterrupt()
        ic_peerEvent.waitForShutdown()
        broker.waitForShutdown()

        topic_peerEvent.unsubscribe(subscriber)

        return 0


server = Server()
sys.exit(server.main(sys.argv))