class ErrorStore:
    
    def __init__(self):
        self.errorstore = []

    def add(self, uri, errordata):
        self.errorstore.append( uri, errordata )

class FileErrorStore(ErrorStore):

    def __init__(self, filename):
        self.filename = filename

        self.filehandle = open(self.filename)

    def __del__(self):
        self.filehandle.close()

    def add(self, uri, errordata):
        self.filehandle.write("{}\t{}\n").format(uri, errordata)

errorstore = ErrorStore()
