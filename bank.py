import json
import helper

balanceFile = 'balances.json'
loanAmount = 100

statSetupInfo = {
    'balance' : { 'display' : 'Balance', 'startAmount' : 100, 'toMoney' : True },
    'totalWon' : { 'display' : 'Money Won', 'startAmount' : 0, 'toMoney' : True },
    'totalLost' : { 'display' : 'Money Lost', 'startAmount' : 0, 'toMoney' : True },
    'totalClaimed' : { 'display' : 'Money Claimed', 'startAmount' : 0, 'toMoney' : True },
    'totalUpgrades' : { 'display' : 'Spent on Upgrades', 'startAmount' : 0, 'toMoney' : True },
    'totalTrinkets' : { 'display' : 'Spent on Trinkets', 'startAmount' : 0, 'toMoney' : True },
    'loans' : { 'display' : 'Loans Given', 'startAmount' : 0, 'toMoney' : False },
    'resets' : { 'display' : 'Balance Hit 0', 'startAmount' : 0, 'toMoney' : False },
    'flipWins' : { 'display' : 'Flip Wins', 'startAmount' : 0, 'toMoney' : False },
    'flipLosses' : { 'display' : 'Flip Losses', 'startAmount' : 0, 'toMoney' : False },
    'rollWins' : { 'display' : 'Roll Wins', 'startAmount' : 0, 'toMoney' : False },
    'rollLosses' : { 'display' : 'Roll Losses', 'startAmount' : 0, 'toMoney' : False },
    #'suitWins' : { 'display' : 'Suit Wins', 'startAmount' : 0, 'toMoney' : False },
    #'suitLosses' : { 'display' : 'Suit Losses', 'startAmount' : 0, 'toMoney' : False },
    'xyzWins' : { 'display' : 'XYZ Wins', 'startAmount' : 0, 'toMoney' : False },
    'xyzLosses' : { 'display' : 'XYZ Losses', 'startAmount' : 0, 'toMoney' : False },
    'fiftyWins' : { 'display' : '50/50 Wins', 'startAmount' : 0, 'toMoney' : False },
    'fiftyLosses' : { 'display' : '50/50 Losses', 'startAmount' : 0, 'toMoney' : False },
    'trinkets' : { 'display' : 'Trinkets', 'startAmount' : 0, 'toMoney' : False },
    'goon1' : { 'display' : 'Goon 1 Lvl', 'startAmount' : 0, 'toMoney' : False },
    'goon2' : { 'display' : 'Goon 2 Lvl', 'startAmount' : 0, 'toMoney' : False },
    'goon3' : { 'display' : 'Goon 3 Lvl', 'startAmount' : 0, 'toMoney' : False },
    'goon4' : { 'display' : 'Goon 4 Lvl', 'startAmount' : 0, 'toMoney' : False },
    'goon5' : { 'display' : 'Goon 5 Lvl', 'startAmount' : 0, 'toMoney' : False },
    'goon6' : { 'display' : 'Goon 6 Lvl', 'startAmount' : 0, 'toMoney' : False }
}


class Bank:   
    def __init__(self):
        self.flipBoxMessages = []
        self.streakBonus = [] #Holds Tuples (userId, totalStreakBonus, -1=lose streak|1=win streak, streakCount)
        self.streakBonusPerWinLoss = 0.09
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
    def getPlayerStats(self, userId):
        id = str(userId)
        self.createNewUserStats(id)

        displayList = []
        valueList = []

        for key in statSetupInfo.keys():
            displayList.append(statSetupInfo[key]['display'])

            if statSetupInfo[key]['toMoney']:
                valueList.append('**' + helper.moneyFormat(str(int(self.balances[id][key]))) + '**')
            else:
                valueList.append('**' + str(self.balances[id][key]) + '**')

        return displayList, valueList


    #Creates a string with all of the stats of the channel
    def getGlobalStats(self):
        displayList = []
        valueList = []

        for stat in statSetupInfo.keys():
            totalStat = 0

            for user in self.balances.keys():
                totalStat += self.balances[user][stat]

            displayList.append(statSetupInfo[stat]['display'])

            if statSetupInfo[stat]['toMoney']:
                valueList.append('**' + helper.moneyFormat(str(int(totalStat))) + '**')
            else:
                valueList.append('**' + str(totalStat) + '**')

        return displayList, valueList


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
                if len(self.flipBoxMessages[i][4]) > 12:
                    self.flipBoxMessages[i][4].clear()

                if result < 0:
                    self.flipBoxMessages[i][4].append(':red_circle:')
                else:
                    self.flipBoxMessages[i][4].append(':green_circle:')
                return


    def getStreakBonus(self, userId):
        for i in range(0, len(self.streakBonus)):
            if userId == self.streakBonus[i][0]:
                return self.streakBonus[i][1], self.streakBonus[i][2]
        return -1,-1


    def startStreakBonus(self, userId, outcome):
        element = [userId, 0.0, outcome, 1]
        self.streakBonus.append(element)

    
    def increaseStreakBonus(self, userId, outcome):
        for i in range(0, len(self.streakBonus)):
            if userId == self.streakBonus[i][0]:
                self.streakBonus[i][3] += 1
                if self.streakBonus[i][3] >= 2:
                    self.streakBonus[i][1] += (self.streakBonusPerWinLoss * outcome)
                    print(self.streakBonus[i][1])
                    if self.streakBonus[i][1] >= abs(0.37):
                        self.resetStreakBonus(userId)

    
    def resetStreakBonus(self, userId):
        for i in range(0, len(self.streakBonus)):
            if userId == self.streakBonus[i][0]:
                self.streakBonus.pop(i)