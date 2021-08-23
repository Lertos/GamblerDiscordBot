import math

#Returns the amount back with proper formatting (such as commas)
def moneyFormat(money):
    return f'{money:,}' + '$'


#Returns a formatted header for any list, given the main text
def listHeaders(text):
    return ':moneybag: :moneybag: :moneybag:   **' + str(text) + '**   :moneybag: :moneybag: :moneybag:\n\n'


def getRollNumberWord(roll):
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