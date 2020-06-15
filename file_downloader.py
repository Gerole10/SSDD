#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from io import open
import Ice
Ice.loadSlice('-I. --all trawlnet.ice') 
import TrawlNet



class PeerEventI(TrawlNet.PeerEvent):
    def peerFinished(self, peerInfo, current = None):
        print("Notificando al transfer")
        peerInfo.transfer.destroyPeer(peerInfo.fileName)

class PeerInfoI(TrawlNet.PeerInfo):
    def __init__(self, transfer, fileName):
        self.transfer = transfer
        self.fileName = fileName

class ReceiverI(TrawlNet.Receiver):
    def __init__(self, fileName, sender, transfer):
        self.fileName = fileName
        self.sender = sender
        self.transfer = transfer
        self.puntero = 0

    def start(self, current = None):
        print("Recevier del archivo: "+self.fileName)
        print(self.sender)
        print(self.transfer)

        ar = open("./files_received/"+self.fileName,"w")

        while True:
            ar.seek(self.puntero)
            lectura = self.sender.receive(10)
            print("Archivo "+self.fileName+" recibiéndose, escribiendo...")
            ar.write(lectura)
            self.puntero += 10
            if len(lectura) < 10:
                print("Transferencia de "+self.fileName+" completada.")
                #Cerrar el archivo falta
                break
        
        #Crear PeerInfo(Transfer, filename)
        #print("Creando peerInfo")
        #peerInfo = PeerInfoI(self.transfer, self.fileName)
        #Crear PeerEvent y llamar a peerFinished
        #print("Creando peerEvent")
        #peerEvent = PeerEventI()
        #print("Llamado metodo peerFinished")
        #peerEvent.peerFinished(peerInfo)


    def destroy(self, current = None):
        print("Destruir receiver")
    
    def getFileName(self, current = None):
        return self.fileName

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

        #Conexion con transferFactory
        proxyTransfer = self.communicator().stringToProxy(argv[1])
        transferFactory = TrawlNet.TransferFactoryPrx.checkedCast(proxyTransfer)

        if not transferFactory:
            raise RuntimeError('Invalid proxy transferFactory')

        #Creacion proxy receiverFactory
        broker = self.communicator()
        servant = ReceiverFactoryI()

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
        receiverList = transfer.createPeers(files)
        print(receiverList)

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