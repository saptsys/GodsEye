import sqlite3
import datetime
import cv2

class Database:
    def __init__(self,path="GodsEye.db"):
        try:
            self.__path = path
            con = self.connection()
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS plates( id INTEGER PRIMARY KEY AUTOINCREMENT, number nvarchar(10) NOT NULL, owner char(255), image BLOB,data json);")
            con.commit()
        except Exception as ex:
            print("Database-ctor Error : "+str(ex))
        finally:
            con.close()
    
    def connection(self):
        try:
            con = sqlite3.connect(self.__path)
            return con
        except Exception as ex:
            print("Database-connection Error : "+str(ex))

    # def insertPlates(self, plates):
    #     try:
    #         con = self.connection()
    #         for plate in plates:
    #             _,enc = cv2.imencode(".jpg",plate[1])
    #             cur = con.cursor()
    #             cv2.imshow('insertig',plate[1])
    #             cur.execute("INSERT INTO plates VALUES(?,?,?,?)",(None,plate[0],enc,None))
    #             con.commit()
    #     except Exception as ex:
    #         print("Database-insertPlate Error : "+str(ex))
    #     finally:
    #         con.close()
    
    def insertPlates(self,number,owner,image,data):
        try:
            con = self.connection()
            _,enc = cv2.imencode(".jpg",image)
            cur = con.cursor()
            cv2.imshow('insertig',image)
            cur.execute("INSERT INTO plates VALUES(?,?,?,?,?)",(None,number,owner,enc,data))
            con.commit()
        except Exception as ex:
            print("Database-insertPlate Error : "+str(ex))
        finally:
            con.close()
        
