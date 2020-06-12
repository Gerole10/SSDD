#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from io import open
import Ice
Ice.loadSlice('-I. --all trawlnet.ice') 
import TrawlNet


class SenderI(TrawlNet.Sender):
    def __init__(self, fileName):
        self.fileName = fileName
        self.puntero = 0

    def receive(self,size,current = None):
        archivo = open("./files_sended/"+self.fileName,"r")
        archivo.seek(self.puntero)
        print("Archivo "+self.fileName+" encontrado, leyendo...")
        self.puntero += size
        return archivo.read(size)

    def close():
        archivo = open(self.fileName,"r") 
        archivo.close()

    def destroy():
        print("Hola")
        sys.stdout.flush()

class SenderFactoryI(TrawlNet.SenderFactory):
    def create(self, fileName, current = None):
        print("Creacion Sender para:"+ fileName)
        servant = SenderI(fileName)
        proxy = current.adapter.addWithUUID(servant)
        return TrawlNet.SenderPrx.checkedCast(proxy)

class Server(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        servant = SenderFactoryI()

        adapter = broker.createObjectAdapter("SenderFactoryAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("senderFactory1"))

        print(proxy, flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))