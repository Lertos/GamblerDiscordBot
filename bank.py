import json
import helper

balanceFile = 'balances.json'
loanAmount = 100

statSetupInfo = {
    'balance' : { 'display' : 'Current Balance', 'startAmount' : 100 },
    'totalWon' : { 'display' : 'Total Money Won', 'startAmount' : 0 },
    'totalLost' : { 'display' : 'Total Money Lost', 'startAmount' : 0 },
    'loans' : { 'display' : 'Loans Given', 'startAmount' : 0 },
    'flipWins' : { 'display' : 'Coin Flip Wins', 'startAmount' : 0 },
    'flipLosses' : { 'display' : 'Coin Flip Losses', 'startAmount' : 0 },
    'rollWins' : { 'display' : 'Dice Roll Wins', 'startAmount' : 0 },
    'rollLosses' : { 'display' : 'Dice Roll Losses', 'startAmount' : 0 },
    'fiftyWins' : { 'display' : '50/50 Wins', 'startAmount' : 0 },
    'fiftyLosses' : { 'display' : '50/50 Losses', 'startAmount' : 0 },
    'trinkets' : { 'display' : 'Trinkets', 'startAmount' : 0 }
}


class Bank:   
    def __init__(self):
        self.balances = self.loadBankBalances(balanceFile)
        self.addNewKeys()


    #Reads the json file containing all balances
    def loadBankBalances(self, fileName):
        with open(fileName) as f:
            return json.load(f)


    #Saves the json file with the updated balances
    def saveBalances(self):
        with open(balanceFile,'w') as f:
            f.write(json.dumps(self.balances))


    #Adds newly added keys to the stats of each player
    def addNewKeys(self):
        changed = False

        for key in statSetupInfo.keys():
            for user in self.balances:
                if key not in self.balances[user]:
                    self.balances[user][key] = statSetupInfo[key]['startAmount']
                    changed = True
        
        #If there were any changes, save the file immediately
        if changed:
            self.saveBalances()


    #Updates the balance of a user and updates stats
    def updateBalance(self, userId, amount):
        id = str(userId)

        if id in self.balances:
            self.balances[id]['balance'] = self.balances[id]['balance'] + amount
            
            #Instead of making users do !loan, just give them 100
            if self.balances[id]['balance'] == 0:
                self.balances[id]['balance'] = loanAmount

            self.updatePlayerTotalStats(id, amount)
            self.saveBalances()


    #Updates the totalWon and totalLost stats of a player based on outcome
    def updatePlayerTotalStats(self, userId, amount):
        if amount > 0:
            #Insert the stat key if it doesnt exist for the user 
            if 'totalWon' not in self.balances[userId]:
                self.balances[userId]['totalWon'] = 0

            self.balances[userId]['totalWon'] = self.balances[userId]['totalWon'] + amount

        elif amount < 0:
            #Insert the stat key if it doesnt exist for the user 
            if 'totalLost' not in self.balances[userId]:
                self.balances[userId]['totalLost'] = 0

            self.balances[userId]['totalLost'] = self.balances[userId]['totalLost'] + abs(amount)


    #Updates stats of a user of a specific game type based on the outcome
    def updatePlayerStats(self, userId, gameType, outcome):
        id = str(userId)
        key = ''

        if outcome == -1:
            key = gameType + 'Losses'
        elif outcome == 1:
            key = gameType + 'Wins'
        
        #Insert the stat key if it doesnt exist for the user 
        if key not in self.balances[id]:
            self.balances[id][key] = 0

        self.balances[id][key] = self.balances[id][key] + 1

        self.saveBalances()


    #Increment the loan stat of a player
    def updateLoanStat(self, userId):
        id = str(userId)

        #Insert the stat key if it doesnt exist for the user 
        if 'loans' not in self.balances[id].keys():
            self.balances[id]['loans'] = 1
        else:
            self.balances[id]['loans'] = self.balances[id]['loans'] + 1

        self.saveBalances()


    #Give players a loan if they are at minimum cash
    def giveUserLoan(self, userId):
        id = str(userId)

        #Check if the player has a zero balance
        if self.balances[id]['balance'] == 0:
            self.balances[id]['balance'] = loanAmount
            self.saveBalances()
            
            return loanAmount
        else:
            return -1


    #If the user is new add them with the default starting amount
    def createNewBalance(self, userId):
        id = str(userId)

        if id not in self.balances:
            self.balances[id] = {}

            for key in statSetupInfo:
                self.balances[id][key] = statSetupInfo[key]['startAmount']

            self.saveBalances()


    #Calculates the leaderboard
    def getLeaderboard(self, userId, members):
        header = helper.listHeaders('TOP BALANCES')

        sortedBalances = sorted(self.balances.items(), key=lambda x: x[1]['balance'], reverse=True)
        formatted = list(map(lambda x: str(helper.moneyFormat(x[1]['balance'])) + ' - ' + helper.getDisplayName(userId, members, x[0]), sortedBalances))

        return header + '\n'.join(formatted)


    #Creates a string with all of the player stats in it
    def getPlayerStats(self, userId, name):
        id = str(userId)
        output = helper.listHeaders('STATS FOR ' + name)

        if id not in self.balances:
            self.createNewBalance(userId)

        for key in statSetupInfo.keys():
            output += '• ' + statSetupInfo[key]['display'] + ': ' + str(self.balances[id][key]) + '\n'

        return output


    #Creates a string with all of the stats of the channel
    def getGlobalStats(self):
        output = helper.listHeaders('GLOBAL STATS')

        for stat in statSetupInfo.keys():
            totalStat = 0

            for user in self.balances.keys():
                totalStat += self.balances[user][stat]

            output += '• ' + statSetupInfo[stat]['display'] + ': ' + str(totalStat) + '\n'

        return output


    #Creates a string with all of the stats of the channel
    def resetPlayerStats(self, userId):
        id = str(userId)

        if id in self.balances:
            changed = False

            for key in statSetupInfo.keys():
                if key in self.balances[id]:
                    self.balances[id][key] = statSetupInfo[key]['startAmount']
                    changed = True
            
            #If there were any changes, save the file immediately
            if changed:
                self.saveBalances()