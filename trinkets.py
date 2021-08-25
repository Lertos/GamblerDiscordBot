import helper


class Trinkets:   
    def __init__(self):
        self.bonusPerLevel = 0.0025
        self.costPerLevel = 500
        self.costMultiplier = 1.25


    #Gets the trinket level given a user id
    def getTrinketLevel(self, userId, balances):
        id = str(userId)

        if id not in balances.keys():
            return -1

        return balances[id]['trinkets']


    #Gets the bonus for the number of trinkets the user has
    def getBonusFromTrinkets(self, userId, balances):
        level = self.getTrinketLevel(userId, balances)

        if level == -1:
            return 0
        else:
            return level * self.bonusPerLevel


    #Gets the price of the next trinket available
    def getNextTrinketPrice(self, userId, balances):
        level = self.getTrinketLevel(userId, balances)
        
        return self.costPerLevel * (self.costMultiplier * (level + 1))


    #Increments the trinket value for the user
    def incrementTrinketAmount(self, userId, balances):
        id = str(userId)

        if id not in balances.keys():
            return

        balances[id]['trinkets'] = balances[id]['trinkets'] + 1


    #Displays the top trinket amounts
    def getTopTrinkets(self, userId, members, balances):
        header = helper.listHeaders('TOP TRINKETS')

        sortedTrinkets = sorted(balances.items(), key=lambda x: x[1]['trinkets'], reverse=True)
        formatted = list(map(lambda x: str(x[1]['trinkets']) + ' - ' + helper.getDisplayName(userId, members, x[0]), sortedTrinkets))

        return header + '\n'.join(formatted)

