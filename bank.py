import json

balanceFile = 'balances.json'
startAmount = 100

class Bank:
    
    def __init__(self):
        self.balances = self.loadBankBalances(balanceFile)

    #Reads the json file containing all balances
    def loadBankBalances(self, fileName):
        with open(fileName) as f:
            return json.load(f)

    #Updates the balance of a user
    def updateBalance(self, userId, amount):
        if str(userId) in self.balances:
            self.balances[str(userId)] = self.balances[str(userId)] + amount
            print(self.balances)
            self.saveBalances()
            print(self.balances)

    #Saves the json file with the updates balances
    def saveBalances(self):
        with open(balanceFile,'w') as f:
            f.write(json.dumps(self.balances))

    #If the user is new add them with the default starting amount
    def createNewBalance(self, userId):
        if str(userId) not in self.balances:
            self.balances[str(userId)] = startAmount
            self.saveBalances()
            print(self.balances)