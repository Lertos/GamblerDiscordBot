import time
import math
import helper

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
    def checkTimeLeftBeforeLoan(self, userId):
        return helper.checkTimeLeft(userId, self.loans, 'You do not have a cooldown and the loan is available')