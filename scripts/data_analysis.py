from PySide6 import QtWidgets
import sys
from PySide6 import QtSql

db = QtSql.QSqlDatabase.addDatabase("QMYSQL")
db.setHostName("airdata.skysquitter.com")
db.setDatabaseName("db_airdata")
db.setUserName("tubs")
db.setPassword("ue73f5dn")
db.open()

q2 = QtSql.QSqlQuery("", db)
q2.exec("select id, timestamp, address from tbl_mode_s where bds = 5 limit 50000")

list = []
while q2.next():
    id = q2.value("id")
    time = q2.value("timestamp").toString()
    address = q2.value("address")
    list.append({"id": id, "time": time, "address": address})

list[2934]
