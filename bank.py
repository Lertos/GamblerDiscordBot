import json
import helper

balanceFile = 'balances.json'

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
    'fiftyLosses' : { 'display' : '50/50 Losses', 'startAmount' : 0 }
}


class Bank:   
    def __init__(self):
        self.balances = self.loadBankBalances(balanceFile)


    #Reads the json file containing all balances
    def loadBankBalances(self, fileName):
        with open(fileName) as f:
            return json.load(f)


    #Saves the json file with the updated balances
    def saveBalances(self):
        with open(balanceFile,'w') as f:
            f.write(json.dumps(self.balances))


    #Updates the balance of a user and updates stats
    def updateBalance(self, userId, amount):
        id = str(userId)

        if id in self.balances:
            self.balances[id]['balance'] = self.balances[id]['balance'] + amount
            
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
        sortedBalances = sorted(self.balances.items(), key=lambda x: x[1]['balance'], reverse=True)
        output = list(map(lambda x: str(helper.moneyFormat(x[1]['balance'])) + ' - ' + self.getDisplayName(userId, members, x[0]), sortedBalances))

        return '\n'.join(output)


    #Creates a string with all of the player stats in it
    def getPlayerStats(self, userId, name):
        id = str(userId)
        output = '===== STATS FOR ' + name + ' =====\n'

        if id not in self.balances:
            self.createNewBalance(userId)

        for key in statSetupInfo.keys():
            output += '• ' + statSetupInfo[key]['display'] + ': ' + str(self.balances[id][key]) + '\n'

        return output

    #Find the users id in the members list and returns the display name 
    def getDisplayName(self, userId, members, id):
        for x,y in members:
            if str(x) == str(id):
                if str(userId) == str(id):
                    return '**' + str(y) + '**'
                else:
                    return y
