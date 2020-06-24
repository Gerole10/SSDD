#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import binascii
import Ice
Ice.loadSlice('-I. --all trawlnet.ice') 
import TrawlNet


class SenderI(TrawlNet.Sender):
    def __init__(self, path, fileName):
        self.path = path
        self.fileName = fileName
        self.file_ = open("./"+self.path+self.fileName, "rb")

        #CAMBIAR y capturar si ya existe
    def receive(self,size,current = None):
        return str(binascii.b2a_base64(self.file_.read(size), newline = False))

    def close(self, current = None):
        print("Cerrando fichero " +self.fileName)
        self.file_.close()

    def destroy(self, current = None):
        try:
            print("Destruido adaptador sender")
            current.adapter.remove(current.id)
        except Exception as e:
            print(e)

class SenderFactoryI(TrawlNet.SenderFactory):
    def __init__(self, path):
            self.path = path

    def create(self, fileName, current = None):
        print("Creacion Sender para:"+ fileName)
        try:
            prueba = open("./"+self.path+fileName, 'rb').readline()
        except IOError:
            print("El archivo \"" +fileName+ "\" no existe.")
            raise TrawlNet.FileDoesNotExistError("El archivo \"" +fileName+ "\" no existe.")
        else:
            servant = SenderI(self.path, fileName)
            proxy = current.adapter.addWithUUID(servant)
            return TrawlNet.SenderPrx.checkedCast(proxy)


class Server(Ice.Application):
    def run(self, argv):
        path = argv[1]
        broker = self.communicator()
        servant = SenderFactoryI(path)

        adapter = broker.createObjectAdapter("SenderFactoryAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("senderFactory1"))

        print(proxy, flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))
