from PySide6 import QtSql

class Database:
    def __init__(self):        
        self.db = QtSql.QSqlDatabase.addDatabase("QMYSQL")
        self.db.setHostName("airdata.skysquitter.com")
        self.db.setDatabaseName("db_airdata")
        self.db.setUserName("tubs")
        self.db.setPassword("ue73f5dn")
        self.open = self.db.open()
        self.q = QtSql.QSqlQuery(self.db)

    def __del__(self):
        self.db.close()

    def isOpen(self):
        return self.open
    
    def close(self):
        self.db.close()
        return not self.db.isOpen()
    
    def query(self, query):
        return self.q.exec(query)

    def getAll(self, elements=[]):
        allResults = []
        q = self.q
        while q.next():
            entry = {}
            for el in elements:
                entry[el] = q.value(el)
            allResults.append(entry)
        
        return allResults
