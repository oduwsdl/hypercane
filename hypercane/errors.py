import logging

module_logger = logging.getLogger('hypercane.errors')

class ErrorStore:

    def __init__(self):
        self.type = None

    def add(self, uri, errordata):
        # print("adding to type {} with output at {}".format(self.type, self.type.output))
        self.type.add(uri, errordata)

class MemoryStore:
    
    def __init__(self):
        self.errorstore = []
        self.output = "___MEMORY___"

    def add(self, uri, errordata):
        module_logger.info("storing error in memory for {}".format(uri))
        self.errorstore.append( ( uri, errordata ) )

class FileErrorStore(ErrorStore):

    def __init__(self, filename):
        self.output = filename
        self.filehandle = open(self.output, 'w')

    def __del__(self):
        self.filehandle.close()

    def add(self, uri, errordata):
        module_logger.info("writing error for {} to {}".format(uri, self.output))
        self.filehandle.write("{}\t{}\n".format(uri, errordata.replace('\n', '\u2028')))

errorstore = ErrorStore()
errorstore.type = MemoryStore()
