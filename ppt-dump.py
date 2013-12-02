#!/usr/bin/env python2
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import sys, os.path, getopt
from msodumper import ole, pptstream, globals, olestream
from msodumper.globals import error

def usage (exname):
    exname = os.path.basename(exname)
    msg = """Usage: %s [options] [ppt file]

Options:
  --help        displays this help message.
"""%exname
    print msg


class PPTDumper(object):

    def __init__ (self, filepath, params):
        self.filepath = filepath
        self.params = params

    def __printDirHeader (self, dirname, byteLen):
        dirname = globals.encodeName(dirname)
        globals.outputln("")
        globals.outputln("="*68)
        globals.outputln("%s (size: %d bytes)"%(dirname, byteLen))
        globals.outputln("-"*68)

    def dump (self):
        file = open(self.filepath, 'rb')
        strm = pptstream.PPTFile(file.read(), self.params)
        file.close()
        strm.printStreamInfo()
        strm.printHeader()
        strm.printDirectory()
        dirnames = strm.getDirectoryNames()
        result = True
        for dirname in dirnames:
            if len(dirname) == 0 or dirname == 'Root Entry':
                continue

            dirstrm = strm.getDirectoryStreamByName(dirname)
            self.__printDirHeader(dirname, len(dirstrm.bytes))
            if  dirname == "PowerPoint Document":
                if not self.__readSubStream(dirstrm):
                    result = False
            elif  dirname == "Current User":
                if not self.__readSubStream(dirstrm):
                    result = False
            elif  dirname == "\x05DocumentSummaryInformation":
                strm = olestream.PropertySetStream(dirstrm.bytes)
                strm.read()
            else:
                globals.dumpBytes(dirstrm.bytes, 512)
        return result

    def __readSubStream (self, strm):
        # read all records in substream
        return strm.readRecords()


def main (args):
    exname, args = args[0], args[1:]
    if len(args) < 1:
        print("takes at least one argument")
        usage(exname)
        return

    params = globals.Params()
    try:
        opts, args = getopt.getopt(args, "h", ["help", "debug", "show-sector-chain"])
        for opt, arg in opts:
            if opt in ['-h', '--help']:
                usage(exname)
                return
            elif opt in ['--debug']:
                params.debug = True
            elif opt in ['--show-sector-chain']:
                params.showSectorChain = True
            else:
                error("unknown option %s\n"%opt)
                usage()

    except getopt.GetoptError:
        error("error parsing input options\n")
        usage(exname)
        return

    dumper = PPTDumper(args[0], params)
    if not dumper.dump():
        error("FAILURE\n")


if __name__ == '__main__':
    main(sys.argv)

# vim:set filetype=python shiftwidth=4 softtabstop=4 expandtab:
