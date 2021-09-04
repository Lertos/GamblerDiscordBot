import json
import helper
import time
import math

goonsFile = 'goons.json'
maxGoonLevel = 45

goonSetup = {
    1 : {
        'costToBuy' : 3000,
        'costPerLevel' : 400,
        'costMultiplier' : 1.12,
        'moneyPerHourPerLevel' : 40,
        'moneyMultiplier' : 1.1
    },
    2 : {
        'costToBuy' : 10000,
        'costPerLevel' : 390,
        'costMultiplier' : 1.14,
        'moneyPerHourPerLevel' : 50,
        'moneyMultiplier' : 1.12
    },
    3 : {
        'costToBuy' : 25000,
        'costPerLevel' : 380,
        'costMultiplier' : 1.16,
        'moneyPerHourPerLevel' : 60,
        'moneyMultiplier' : 1.14
    },
    4 : {
        'costToBuy' : 75000,
        'costPerLevel' : 370,
        'costMultiplier' : 1.18,
        'moneyPerHourPerLevel' : 70,
        'moneyMultiplier' : 1.16
    },
    5 : {
        'costToBuy' : 150000,
        'costPerLevel' : 360,
        'costMultiplier' : 1.2,
        'moneyPerHourPerLevel' : 80,
        'moneyMultiplier' : 1.18
    },
    6 : {
        'costToBuy' : 400000,
        'costPerLevel' : 350,
        'costMultiplier' : 1.22,
        'moneyPerHourPerLevel' : 90,
        'moneyMultiplier' : 1.2
    }
}


class Goons:   
    def __init__(self):
        self.goonClaimTimes = self.loadGoonClaimTimes(goonsFile)


    #Reads the json file containing all goon cooldowns
    def loadGoonClaimTimes(self, fileName):
        with open(fileName) as f:
            return json.load(f)


    #Saves the json file with the updated goon cooldowns
    def saveGoonClaimTimes(self):
        with open(goonsFile,'w') as f:
            f.write(json.dumps(self.goonClaimTimes))


    #Gets the levels of all owned goons and returns them in a dict
    def getGoonLevels(self, player):
        goons = {}

        for i in range(1, len(goonSetup.keys()) + 1):
            goons[i] = player['goon' + str(i)]

        return goons


    #Gets the levels of all owned goons
    def getGoonStats(self, player):
        goons = self.getGoonLevels(player)
        outCurrent = []
        outNext = []
        outCost = []
        totalPerHour = 0

        for i in goons:
            currentPerHour = round(goonSetup[i]['moneyPerHourPerLevel'] * (goonSetup[i]['moneyMultiplier'] ** goons[i]))
            nextPerHour = round(goonSetup[i]['moneyPerHourPerLevel'] * (goonSetup[i]['moneyMultiplier'] ** (goons[i]+1)))
            upgradePrice = round(goonSetup[i]['costPerLevel'] * (goonSetup[i]['costMultiplier'] ** (goons[i]+1)))

            if goons[i] == 0:
                outCurrent.append(helper.getNumberEmojiFromInt(i) + ' **' + str(goons[i]) + '**')
            else:
                outCurrent.append(helper.getNumberEmojiFromInt(i) + ' **' + str(goons[i]) + '** - ' + helper.moneyFormat(str(currentPerHour)) + '/h')
                totalPerHour += currentPerHour
                
            outNext.append(helper.moneyFormat(str(nextPerHour)) + '/h')
            outCost.append(helper.moneyFormat(str(upgradePrice)))

        return outCurrent, outNext, outCost, helper.moneyFormat(str(totalPerHour))


    #Returns the time in seconds since Goon earnings have been claimed
    def getTimeSinceClaimed(self, userId):
        id = str(userId)

        #Check if the user is in the list
        if id not in self.goonClaimTimes:
            return -1

        #Get the total time in seconds and parse it
        cooldownDone = self.goonClaimTimes[id]
        timeInSeconds = round(time.time()) - cooldownDone

        return timeInSeconds


    #Claim the earnings of all owned goons based on the last time 
    def claimGoonIncome(self, userId, balances):
        id = str(userId)

        timeSinceClaimed = self.getTimeSinceClaimed(userId)

        #Check if the player has claimed yet
        if timeSinceClaimed == -1:
            return -1

        #Get the players goon levels
        goons = self.getGoonLevels(balances[id])
        totalAmount = 0

        for goon in goons:
            cashPerHour = goonSetup[goon]['moneyPerHourPerLevel'] * (goonSetup[goon]['moneyMultiplier'] ** goons[goon])
            cashPerSecond = cashPerHour / 3600
            totalCashFromGoon = math.floor(timeSinceClaimed * cashPerSecond)

            totalAmount += totalCashFromGoon

        #If there was at least 1$ to claim, set the last claimed date
        if totalAmount != 0:
            self.goonClaimTimes[id] = round(time.time())
            self.saveGoonClaimTimes()

        return totalAmount


    #Gets the price of the given goon number
    def getNextAvailableGoon(self, userId, balances):
        id = str(userId)
        nextGoon = 0
        numberOfGoons = len(goonSetup.keys())

        for i in range(1, numberOfGoons + 1):
            nextGoon = i
            level = balances[id]['goon' + str(i)]
            
            #If the level is zero, then we know we have the highest
            if level == 0:
                break

            #If every goon has been purchased, return -1
            if i == numberOfGoons and level != 0:
                return (-1,-1)

        return (nextGoon, goonSetup[nextGoon]['costToBuy'])


    #Gets the price of the next upgrade for a specific goon
    def getGoonUpgradePrice(self, userId, balances, goonNumber):
        id = str(userId)
        goon = int(goonNumber)

        currentGoonLevel = balances[id]['goon' + str(goon)]

        if currentGoonLevel == maxGoonLevel:
            return -1

        return round(goonSetup[goon]['costPerLevel'] * (goonSetup[goon]['costMultiplier'] ** (currentGoonLevel + 1)))


    #Increments the level of a specific goon
    def incrementGoonAmount(self, userId, balances, goonNumber):
        id = str(userId)
        goon = str(goonNumber)

        #If this is the first purchase of a Goon, make sure they are in the list so that !claim will work
        if id not in self.goonClaimTimes:
            self.goonClaimTimes[id] = round(time.time())
            self.saveGoonClaimTimes()

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


