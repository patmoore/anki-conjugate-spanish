
class Storage(object):
    def __init__(self, db):
        self.db = db
        
    def addSchema(self, tableName, definitionString):
        self.db.executescript("""create table if not exists conjug_es_""" + tableName + 
            """(id              integer primary key,""" +
            definitionString+");")
   