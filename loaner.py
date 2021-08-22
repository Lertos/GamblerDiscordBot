import time
import math

loanAmount = 100
secondsToWait = 600


class Loaner:
    def __init__(self):
        self.loans = {}


    #Returns the loan amount if available - if not returns a negative value
    def askForLoan(self, userId):
        #If the user exists in the file check the cooldown
        if str(userId) in self.loans:
            loanReady = self.loans[str(userId)]
            difference = loanReady - round(time.time())

            #If the cooldown isn't met send back a negative value to show its not ready
            if difference > 0:
                return -1

        #The loan is available so return the amount and set the cooldown
        self.loans[str(userId)] = round(time.time()) + secondsToWait

        return loanAmount


    #Returns the time in hours, minutes, seconds until a loan is available
    def checkTimeLeft(self, userId):
        #Check if the user is in the list
        if str(userId) not in self.loans:
            return 'You do not have a cooldown and the loan is available'

        #Get the total time in seconds and parse it
        loanReady = self.loans[str(userId)]
        totalTime = loanReady - round(time.time())

        hours = math.floor(totalTime / 3600)
        totalTime = totalTime - (hours * 3600)

        minutes = math.floor(totalTime / 60)
        totalTime = totalTime - (minutes * 60)

        return f'You can loan in {hours} hour(s), {minutes} minute(s), {totalTime} second(s)'
