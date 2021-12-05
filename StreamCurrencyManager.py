import os
import json
import pickle

class CurrencyManager():
    filepath: str
    usercurr: dict #store this in memory(?) so I dont write to file every second
    """
    functionality:
     1. stores currency in a file. Probably binary. Can be compressed but no need.
     2. when called - returns currency of specific user
     3. something to do with currency?
    """
    def __init__(self, fpath: str):
        # should init the file here. If it doesn't exist - create empty one.
        self.filepath = fpath+'\\currency.dat'
        if not os.path.isfile(self.filepath):
            newfile = open(self.filepath, 'x')
        newfile = open(self.filepath, 'rb')
        try:
            self.usercurr = pickle.load(newfile)
        except:
            print("Empty stream currency file. Skipping.")
            self.usercurr = dict()
        newfile.close()
        return

    def GrantCurrency(self, user, amount: int):
        if user["name"] in self.usercurr:
            self.usercurr[user["name"]]["currency"] = max(self.usercurr[user["name"]]["currency"]+amount, 0)
            if self.usercurr[user["name"]]["id"] == -1 and "id" in user and user["id"] != -1: self.usercurr[user["name"]]["id"] = user["id"]
        else:
            if "id" not in user: user["id"] = -1 #potentially error in username. Maybe make a function which can lookup and delete such records.
            self.usercurr[user["name"]] = {"id" : user["id"], "currency" : max(amount, 0)}

        #passed a user object and parses it here.
        """prototype of user:
        {
            "id": '55828',
            "name": 'dfcz',
            "rights": 20,
            "premium": false,
            "payments": 'null',
            "mobile": false,
            "hidden": false
        }

        prototype of what it should write in a file:
        "name": 
        {"id": "id", 
        "currency": int(amount of currency)
        }
        """

        return

    def LookupCurrency(self, username) -> int:
        if username not in self.usercurr: return -1
        else: return self.usercurr[username]["currency"]
        #shows currency based on passed user name

    def SaveIntoFile(self):
        #saves self.usercurr into file located at self.filepath
        #if file doesn't exist due to something happening during runtime - creates it first
        if not os.path.isfile(self.filepath):
            newfile = open(self.filepath, 'x')
        newfile = open(self.filepath, 'wb')
        pickle.dump(self.usercurr, newfile)
        newfile.close()
        return
