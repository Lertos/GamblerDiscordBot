import helper


maxGoonLevel = 50

goonSetup = {
    1 : {
        'costPerLevel' : 500,
        'costMultiplier' : 1.25,
        'moneyPerHourPerLevel' : 100
    },
    2 : {
        'costPerLevel' : 500,
        'costMultiplier' : 1.25,
        'moneyPerHourPerLevel' : 100
    },
    3 : {
        'costPerLevel' : 500,
        'costMultiplier' : 1.25,
        'moneyPerHourPerLevel' : 100
    },
    4 : {
        'costPerLevel' : 500,
        'costMultiplier' : 1.25,
        'moneyPerHourPerLevel' : 100
    },
    5 : {
        'costPerLevel' : 500,
        'costMultiplier' : 1.25,
        'moneyPerHourPerLevel' : 100
    },
    6 : {
        'costPerLevel' : 500,
        'costMultiplier' : 1.25,
        'moneyPerHourPerLevel' : 100
    }
}


class Goons:   
    def __init__(self):
        pass


    #Gets the levels of all owned goons
    def getGoonLevels(self, userId, player):
        id = str(userId)
        numberOfGoons = len(goonSetup.keys())
        output = ''

        for i in range(1, numberOfGoons + 1):
            goonLevel = player['goon' + str(i)]

            output += '• Goon ' + str(i) + '   (CURRENT: Lvl. ' + str(goonLevel) + '  |  ' + helper.moneyFormat(str(goonSetup[i]['moneyPerHourPerLevel'] * goonLevel)) + '/h)\n'

        return output


    #Gets the bonus for the number of trinkets the user has
    def claimGoonIncome(self, userId, balances):
        level = self.getTrinketLevel(userId, balances)

        if level == -1:
            return 0
        else:
            return level 


    #Gets the price of the given goon number
    def getNextAvailableGoon(self, userId, balances):
        id = str(userId)
        nextGoon = 0
        numberOfGoons = len(goonSetup.keys())

        for i in range(1, numberOfGoons + 1):
            nextGoon = i
            
            #If the level isnt zero, then we know we have the highest
            if balances[id]['goon' + str(i)] == 0:
                #If every goon has been purchased, return -1
                if i == numberOfGoons:
                    return (-1,-1)
                break

        return (nextGoon, goonSetup[nextGoon]['costPerLevel'] * goonSetup[nextGoon]['costMultiplier'])


    #Gets the price of the next upgrade for a specific goon
    def getGoonUpgradePrice(self, userId, balances, goonNumber):
        id = str(userId)
        goon = int(goonNumber)

        currentGoonLevel = balances[id]['goon' + str(goon)]
        return goonSetup[goon]['costPerLevel'] * (goonSetup[goon]['costMultiplier'] * (currentGoonLevel + 1))


    #Increments the level of a specific goon
    def incrementGoonAmount(self, userId, balances, goonNumber):
        id = str(userId)
        goon = str(goonNumber)

        balances[id]['goon' + goon] = balances[id]['goon' + goon] + 1


    #Displays the top levels of a specific goon
    def getTopGoonLevels(self, userId, members, balances, goonNumber):
        header = helper.listHeaders('TOP GOON ' + str(goonNumber) + ' LEVELS')

        sortedGoons = sorted(balances.items(), key=lambda x: x[1]['goon' + str(goonNumber)], reverse=True)
        formatted = list(map(lambda x: str(x[1]['goon' + str(goonNumber)]) + ' - ' + helper.getDisplayName(userId, members, x[0]), sortedGoons))

        return header + '\n'.join(formatted)


    #Get the max level so players cannot go over
    def getMaxGoonLevel(self):
        return maxGoonLevel


