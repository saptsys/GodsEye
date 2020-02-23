import json
import os
class Settings(dict):
    def __init__(self,filename = "settings.json"):
        
        self.update({
            "windowName":"God's Eye",
            "source":0,
            "dataBase":"GodsEye.db",
            "tesseract":"C:/Program Files/Tesseract-OCR/tesseract.exe",
            "storage":"/",
        })
        
        try:
            self.update(self.load(filename))
        except FileNotFoundError as ex:
            try:
                with open(filename,'w') as file:
                    json.dump(self,file,indent=2)
                self.update(self.load(filename))
                print("--> 'settings.json' file created, you can change your settings. <--")
            except FileNotFoundError as sub_ex:
                print("Settings Not Found")
                exit(0)
        
        if str(self["storage"]).strip() == "/":
            self["storage"] = os.getcwd()+"\\storage"
        

    def load(self,path):
        data = {}
        with open(path,'r') as file:
            try:
                data = json.load(file)
                canUpdate = False
                for key,value in self.items():
                    if(not data.__contains__(key)):
                        canUpdate = True
                        data[key] = value
            except json.decoder.JSONDecodeError as ex:
                print("Settings are not proper formatted in 'settings' file.")
                exit(0)
        
        if canUpdate:
            with open(path,'w') as file:
                json.dump(data,file,indent=2)
        
        return data
