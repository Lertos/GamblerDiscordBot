import time
import math

loanAmount = 1000
secondsToWait = 300


class Loaner:
    def __init__(self):
        self.loans = {}


    #Returns the loan amount if available - if not returns a negative value
    def askForLoan(self, userId):
        id = str(userId)

        #If the user exists in the file check the cooldown
        if id in self.loans:
            loanReady = self.loans[id]
            difference = loanReady - round(time.time())

            #If the cooldown isn't met send back a negative value to show its not ready
            if difference > 0:
                return -1

        #The loan is available so return the amount and set the cooldown
        self.loans[id] = round(time.time()) + secondsToWait

        return loanAmount


    #Returns the time in hours, minutes, seconds until a loan is available
    def checkTimeLeft(self, userId):
        id = str(userId)

        #Check if the user is in the list
        if id not in self.loans:
            return 'You do not have a cooldown and the loan is available'

        #Get the total time in seconds and parse it
        loanReady = self.loans[id]
        totalTime = loanReady - round(time.time())

        hours = math.floor(totalTime / 3600)
        totalTime = totalTime - (hours * 3600)

        minutes = math.floor(totalTime / 60)
        totalTime = totalTime - (minutes * 60)

        return f'You can loan in {hours} hour(s), {minutes} minute(s), {totalTime} second(s)'
