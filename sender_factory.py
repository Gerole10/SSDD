#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from io import open
import Ice
Ice.loadSlice('-I. --all trawlnet.ice') 
import TrawlNet


class SenderI(TrawlNet.Sender):
    archivo = ""

    def __init__(self, fileName):
        self.fileName = fileName
        self.puntero = 0
        

    def receive(self,size,current = None):
        self.archivo = open("./files_sended/"+self.fileName,"r")
        self.archivo.seek(self.puntero)
        print("Archivo "+self.fileName+" encontrado, leyendo...")
        self.puntero += size
        return self.archivo.read(size)

    def close(self, current = None):
        print("Cerrando fichero " +self.fileName)
        self.archivo.close()

    def destroy(self, current = None):
        try:
            print("Destruido adaptador sender")
            current.adapter.remove(current.id)
        except Exception as e:
            print(e)

class SenderFactoryI(TrawlNet.SenderFactory):
    def create(self, ruta, fileName, current = None):
        print("Creacion Sender para:"+ fileName)

        try:
            prueba = open("./"+ruta+"/"+fileName, 'r').readline() #Pensado para que introduzca la ruta como el nombre de la carpeta 
            #y ésta debe estar en el mismo directorio que el resto de archivos
        except IOError:
            print("El archivo \"" +fileName+ "\" no existe.")
            raise TrawlNet.FileDoesNotExistError("El archivo \"" +fileName+ "\" no existe.")
        else:
            servant = SenderI(fileName)
            proxy = current.adapter.addWithUUID(servant)
            return TrawlNet.SenderPrx.checkedCast(proxy)


class Server(Ice.Application):
    ruta = ""
    def run(self, argv):
        self.ruta = argv[2]
        broker = self.communicator()
        servant = SenderFactoryI(self.ruta)

        adapter = broker.createObjectAdapter("SenderFactoryAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("senderFactory1"))

        print(proxy, flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))
