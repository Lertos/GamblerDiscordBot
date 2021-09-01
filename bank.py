import json
import helper

balanceFile = 'balances.json'
loanAmount = 100

statSetupInfo = {
    'balance' : { 'display' : 'Current Balance', 'startAmount' : 100 },
    'totalWon' : { 'display' : 'Total Money Won', 'startAmount' : 0 },
    'totalLost' : { 'display' : 'Total Money Lost', 'startAmount' : 0 },
    'loans' : { 'display' : 'Loans Given', 'startAmount' : 0 },
    'resets' : { 'display' : 'Times Balance Hit ZERO', 'startAmount' : 0 },
    'flipWins' : { 'display' : 'Coin Flip Wins', 'startAmount' : 0 },
    'flipLosses' : { 'display' : 'Coin Flip Losses', 'startAmount' : 0 },
    'rollWins' : { 'display' : 'Dice Roll Wins', 'startAmount' : 0 },
    'rollLosses' : { 'display' : 'Dice Roll Losses', 'startAmount' : 0 },
    'suitWins' : { 'display' : 'Suit Wins', 'startAmount' : 0 },
    'suitLosses' : { 'display' : 'Suit Losses', 'startAmount' : 0 },
    'xyzWins' : { 'display' : 'XYZ Wins', 'startAmount' : 0 },
    'xyzLosses' : { 'display' : 'XYZ Losses', 'startAmount' : 0 },
    'fiftyWins' : { 'display' : '50/50 Wins', 'startAmount' : 0 },
    'fiftyLosses' : { 'display' : '50/50 Losses', 'startAmount' : 0 },
    'trinkets' : { 'display' : 'Trinkets', 'startAmount' : 0 },
    'goon1' : { 'display' : 'Goon 1 Level', 'startAmount' : 0 },
    'goon2' : { 'display' : 'Goon 2 Level', 'startAmount' : 0 },
    'goon3' : { 'display' : 'Goon 3 Level', 'startAmount' : 0 },
    'goon4' : { 'display' : 'Goon 4 Level', 'startAmount' : 0 },
    'goon5' : { 'display' : 'Goon 5 Level', 'startAmount' : 0 },
    'goon6' : { 'display' : 'Goon 6 Level', 'startAmount' : 0 }
}


class Bank:   
    def __init__(self):
        self.flipBoxMessages = []
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


    #If the user is new add them with default starting amounts
    def createNewUserStats(self, userId):
        id = str(userId)

        if id not in self.balances:
            self.balances[id] = {}

            for key in statSetupInfo:
                self.balances[id][key] = statSetupInfo[key]['startAmount']

            self.saveBalances()


    #Update player stat given the userId, key and value to add
    def updatePlayerStat(self, userId, key, valueToAdd):
        id = str(userId)
        self.createNewUserStats(id)

        self.balances[id][key] = self.balances[id][key] + valueToAdd
        self.saveBalances()


    #Updates the balance of a user and updates stats
    def updateBalance(self, userId, amount, updateTotal = True):
        id = str(userId)
        self.createNewUserStats(id)

        self.balances[id]['balance'] = self.balances[id]['balance'] + amount
        
        if self.balances[id]['balance'] == 0:
            #self.balances[id]['balance'] = loanAmount
            self.updatePlayerStat(id, 'resets', 1)

        if amount > 0 and updateTotal:
            self.balances[id]['totalWon'] = self.balances[id]['totalWon'] + amount
        elif amount < 0 and updateTotal:
            self.balances[id]['totalLost'] = self.balances[id]['totalLost'] + abs(amount)

        self.saveBalances()


    #Updates stats of a user of a specific game type based on the outcome
    def updateModeStats(self, userId, gameType, outcome):
        if outcome == -1:
            self.updatePlayerStat(userId, gameType + 'Losses', 1)
        elif outcome == 1:
            self.updatePlayerStat(userId, gameType + 'Wins', 1)


    #Calculates the leaderboard based on balances
    def getTopBalances(self, userId, members):
        header = helper.listHeaders('TOP BALANCES')

        sortedBalances = sorted(self.balances.items(), key=lambda x: x[1]['balance'], reverse=True)
        formatted = list(map(lambda x: str(helper.moneyFormat(x[1]['balance'])) + ' - ' + helper.getDisplayName(userId, members, x[0]), sortedBalances))

        return header + '\n'.join(formatted)


    #Creates a string with all of the player stats in it
    def getPlayerStats(self, userId, name):
        id = str(userId)
        self.createNewUserStats(id)

        output = helper.listHeaders('STATS FOR ' + name)

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


    #Returns the players stats dict
    def getPlayerStatDict(self, userId):
        id = str(userId)
        self.createNewUserStats(id)

        return self.balances[id]


    def getFlipBoxMessages(self):
        return self.flipBoxMessages

    
    def getFlipBoxMessageIds(self):
        return [tup[0] for tup in self.flipBoxMessages]


    def getFlipBoxMessage(self, messageId):
        for i in range(0, len(self.flipBoxMessages)):
            if self.flipBoxMessages[i][0] == messageId:
                return self.flipBoxMessages[i]


    def addFlipBoxMessage(self, messageId, userId, name, amount):
        self.flipBoxMessages.append((messageId, str(userId), name, amount, []))


    def addFlipBoxResult(self, messageId, result):
        for i in range(0, len(self.flipBoxMessages)):
            if self.flipBoxMessages[i][0] == messageId:
                if result < 0:
                    self.flipBoxMessages[i][4].append(':red_circle:')
                else:
                    self.flipBoxMessages[i][4].append(':green_circle:')
                return