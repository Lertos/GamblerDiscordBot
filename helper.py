import math
from random import choice

#Returns the amount back with proper formatting (such as commas)
def moneyFormat(money):
    return f'{money:,}' + '$'


#Returns a formatted header for any list, given the main text
def listHeaders(text):
    return ':moneybag: :moneybag: :moneybag:   **' + str(text) + '**   :moneybag: :moneybag: :moneybag:\n\n'


#Used to show dice rolls as discord emojis given an integer dice result
def getRollNumberWord(isWinner, guess):
    sides = [1,2,3,4,5,6]

    if isWinner == False:
        sides.remove(int(guess))
        roll = choice(sides)
    else:
        roll = guess

    if roll == 1:
        return ':one:'
    elif roll == 2:
        return ':two:'
    elif roll == 3:
        return ':three:'
    elif roll == 4:
        return ':four:'
    elif roll == 5:
        return ':five:'
    elif roll == 6:
        return ':six:'


#Find the users id in the members list and returns the display name 
def getDisplayName(userId, members, id):
    for x,y in members:
        if str(x) == str(id):
            if str(userId) == str(id):
                return '**' + str(y) + '**'
            else:
                return y