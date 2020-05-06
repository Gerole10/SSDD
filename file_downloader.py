#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('-I. --all Trawlnet.ice') 
import Trawlnet


class Client(Ice.Application):
    def run(self, argv):
        proxy = self.communicator().stringToProxy(argv[1])
        TransFactory = Example.TransferFactoryPrx.checkedCast(proxy)

        if not factory:
            raise RuntimeError('Invalid proxy')

        #adapter = broker.createObjectAdapter("PrinterAdapter")
        #proxy = adapter.add(servant, broker.stringToIdentity("printer1"))

        printer = factory.make("transfer1")
        printer.write('Conseguido!')

        return 0


sys.exit(Client().main(sys.argv))