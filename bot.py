import os
import discord
import bank
import helper
import fifty
import loaner
import trinkets
import goons
import gameEmbed

from random import randrange, choice, random
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#Enable intents so the member list can be accessed
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

botBank = bank.Bank()
botLoaner = loaner.Loaner()
botFifty = fifty.FiftyFifty()
botTrinkets = trinkets.Trinkets()
botGoons = goons.Goons()
botGameEmbed = gameEmbed.GameEmbed()

#Setup variables
flipPayoutRate = 1
rollPayoutRate = 5
suitPayoutRate = 3
xyzPayoutRate = 2


#================
#   ON READY
#===============================================
@bot.event
async def on_ready():
    print(f'---------  {bot.user} has started   ---------')


#===============================================
#   ON_COMMAND_ERROR 
#===============================================
@bot.event
async def on_command_error(ctx, exception):
    #Checks for any errors in the command syntax
    if isinstance(exception, commands.MissingRequiredArgument) or isinstance(exception, commands.UserInputError):
        cmds = ctx.command.aliases
        cmds.append(ctx.command.name)

        await ctx.channel.send('**The proper command usage is:**  ![' + ' | '.join(cmds) + '] ' + ctx.command.help)

    #Checks to make sure the required permissions are had
    if isinstance(exception, commands.CheckFailure):
        await ctx.channel.send('You do not have the required role to execute that command')


#===============================================
#   Validation checks for any type of betting
#===============================================
def validation(userId, amount):
    resultMsg = ''

    #Create new balance if user doesn't exist yet
    botBank.createNewUserStats(userId)

    #Check to make sure the amount is positive
    if amount <= 0:
        resultMsg = 'The amount supplied must be over 0$'

    #Check to make sure the user has enough money
    elif botBank.balances[str(userId)]['balance'] < amount:
        resultMsg = 'You do not have enough money'

    return resultMsg


#===============================================
#   Gets the payout based on if the guess was correct
#===============================================
def getPayoutResult(userId, amount, multiplier, result):
    #Calculate the payout to the user
    if result == True:
        payout = amount * multiplier
    else:
        payout = -amount

    #Add the payout to the users balance
    botBank.updateBalance(userId, payout)

    return payout


#===============================================
#   Returns the users unique ID based on given display name or -1 if not found
#===============================================
async def getIdFromDisplayName(ctx, displayName):
    async for member in ctx.guild.fetch_members(limit=None):
        if displayName.lower() == member.display_name.lower():
            return member.id  
    return -1


#===============================================
#   Returns the user object based on given user id
#===============================================
async def getUserFromId(ctx, userId):
    id = int(userId)

    async for member in ctx.guild.fetch_members(limit=None):
        if id == member.id:
            return member
    return -1


#===============================================
#   Randomly generates a number and checks the win condition
#===============================================
def isWinner(userId, balances, chanceToWin):
    result = random()

    #Get the players additional chance of winning
    bonus = botTrinkets.getBonusFromTrinkets(userId, balances)
    
    #Since games have different % chance to win - need to normalize it for the mode
    normalizedBonus = bonus * chanceToWin

    #Check if the user scored above the chance of winning
    if result <= (chanceToWin + normalizedBonus):
        return True
    return False


#===============================================
#   Processes the fifty game mode outcome
#===============================================
async def processFiftyFifty(ctx, userId, opponentName, result, amount, isPoster):
    payout = amount * result
    outcome = 'WON'

    #If its a loss - only the challenger loses money
    if result == -1:
        outcome = 'LOST'

        if not isPoster:
            botBank.updateBalance(userId, payout)
    #If its a win - the poster gets double the payout
    else:
        if not isPoster:
            botBank.updateBalance(userId, payout)
        else:
            botBank.updateBalance(userId, payout * 2)

    botBank.updateModeStats(userId, 'fifty', result)

    #Send the results to the poster as they may not be online
    if isPoster:
        userObj = await getUserFromId(ctx, userId)
        await ctx.channel.send(userObj.mention + ' You have **' + outcome + '** against **' + opponentName.capitalize() + '**   (**BET: ' + str(helper.moneyFormat(abs(amount))) + '**)')


#===============================================
#   FLIP
#===============================================
@bot.command(name='flip', aliases=["f"], help='[h | t] [bet amount]', brief='[h | t] [bet amount] - Flips a coin (1/2 chance, 2 * payout)',  ignore_extra=True) 
async def flipCoin(ctx, guess : str, amount : int):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    choices = ['h','t']

    #Check to make sure the player supplied either a 'h' or a 't'
    if guess not in choices:
        await ctx.channel.send(name + ', you must supply either ''h'' (heads) or ''t'' (tails)')
        return

    #Checks for any errors of the input
    resultMsg = validation(userId, amount)

    if resultMsg != '':
        await ctx.channel.send(resultMsg)
        return

    result = isWinner(userId, botBank.balances, 0.5)

    if result == False:
        choices.remove(guess)

    payout = getPayoutResult(userId, amount, flipPayoutRate, result)

    #Send the user the message of the payout and whether they won
    if payout < 0:
        botBank.updateModeStats(userId, 'flip', -1)
        await ctx.channel.send(':regional_indicator_' + choices[0] + ':  ' + name + ', you **LOST**... **' + str(helper.moneyFormat(abs(payout))) + '** has been removed from your balance')
    else:
        botBank.updateModeStats(userId, 'flip', 1)
        await ctx.channel.send(':regional_indicator_' + guess + ':  ' + name + ', you **WON**! **' + str(helper.moneyFormat(abs(payout + amount))) + '** has been added to your balance')


#===============================================
#   ROLL
#===============================================
@bot.command(name='roll', aliases=["r","ro"], help='[1 - 6] [bet amount]', brief='[1-6] [bet amount] Rolls a dice (1/6 chance, 6 * payout)', ignore_extra=True) 
async def rollDice(ctx, guess : int, amount : int):
    #Check to make sure the player supplied either a valid die side
    if guess < 1 or guess > 6:
        await ctx.channel.send('You must supply a number between 1-6')
        return

    userId = ctx.author.id
    name = str(ctx.author.display_name)

    #Checks for any errors of the input
    resultMsg = validation(userId, amount)

    if resultMsg != '':
        await ctx.channel.send(resultMsg)
        return

    result = isWinner(userId, botBank.balances, 0.16666)
    
    payout = getPayoutResult(userId, amount, rollPayoutRate, result)

    #Send the user the message of the payout and whether they won
    if payout < 0:
        botBank.updateModeStats(userId, 'roll', -1)
        await ctx.channel.send(helper.getRollNumberWord(False, guess) + '  ' + name + ', you guessed ' + str(guess) + ' and **LOST**... **' + str(helper.moneyFormat(abs(payout))) + '** has been removed from your balance')
    else:
        botBank.updateModeStats(userId, 'roll', 1)
        await ctx.channel.send(helper.getRollNumberWord(True, guess) + '  ' + name + ', you guessed ' + str(guess) + ' and **WON**! **' + str(helper.moneyFormat(abs(payout + amount))) + '** has been added to your balance')


#===============================================
#   SUIT
#===============================================
@bot.command(name='suit', aliases=["s"], help='[h|s|d|c] [bet amount]', brief='[h|s|d|c] [bet amount] - Chooses a random suit from a deck of cards (1/4 chance, 4 * payout)',  ignore_extra=True) 
async def chooseSuit(ctx, guess : str, amount : int):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    choices = ['h','s','d','c']

    #Check to make sure the player supplied either a 'h' or a 't'
    if guess not in choices:
        await ctx.channel.send(name + ', you must supply either ''h'' (hearts), ''s'' (spades), ''d'' (diamonds), or ''c'' (clubs)')
        return

    #Checks for any errors of the input
    resultMsg = validation(userId, amount)

    if resultMsg != '':
        await ctx.channel.send(resultMsg)
        return

    result = isWinner(userId, botBank.balances, 0.25)

    if result == False:
        choices.remove(guess)

    payout = getPayoutResult(userId, amount, suitPayoutRate, result)

    #Send the user the message of the payout and whether they won
    if payout < 0:
        botBank.updateModeStats(userId, 'suit', -1)
        suit = helper.getCardSuit(False, guess)
        await ctx.channel.send(helper.getNumberEmojiFromInt(randrange(1,14)) + ' of ' + suit + '  ' + name + ', you guessed ' + suit + ' and **LOST**... **' + str(helper.moneyFormat(abs(payout))) + '** has been removed from your balance')
    else:
        botBank.updateModeStats(userId, 'suit', 1)
        suit = helper.getCardSuit(True, guess)
        await ctx.channel.send(helper.getNumberEmojiFromInt(randrange(1,14)) + ' of ' + suit + '  ' + name + ', you guessed ' + suit + ' and **WON**! **' + str(helper.moneyFormat(abs(payout + amount))) + '** has been added to your balance')


#===============================================
#   XYZ
#===============================================
@bot.command(name='x', aliases=["y","z"], help='[bet amount]', brief='[bet amount] - Chooses X, Y, or Z (1/3 chance, 3 * payout)',  ignore_extra=True) 
async def chooseXYZ(ctx, amount : int):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    choices = ['x','y','z']
    guess = ctx.invoked_with[0]

    #Checks for any errors of the input
    resultMsg = validation(userId, amount)

    if resultMsg != '':
        await ctx.channel.send(resultMsg)
        return

    result = isWinner(userId, botBank.balances, 0.33333)

    if result == False:
        choices.remove(guess)

    payout = getPayoutResult(userId, amount, xyzPayoutRate, result)

    #Send the user the message of the payout and whether they won
    if payout < 0:
        botBank.updateModeStats(userId, 'xyz', -1)
        await ctx.channel.send(':regional_indicator_' + choice(choices) + ':  ' + name + ', you **LOST**... **' + str(helper.moneyFormat(abs(payout))) + '** has been removed from your balance')
    else:
        botBank.updateModeStats(userId, 'xyz', 1)
        await ctx.channel.send(':regional_indicator_' + str(guess).lower() + ':  ' + name + ', you **WON**! **' + str(helper.moneyFormat(abs(payout + amount))) + '** has been added to your balance')


#===============================================
#   50create - Creates a new 50/50 posting
#===============================================
@bot.command(name='50create', aliases=['fc'], help='[bet amount]', brief='[bet amount] - Creates a new 50/50 posting',  ignore_extra=True) 
async def fiftyCreate(ctx, amount : int):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    #Checks for any errors of the input
    resultMsg = validation(userId, amount)

    if resultMsg != '':
        await ctx.channel.send(resultMsg)
        return

    #Check if there is already a posting for this user
    hasPosting = botFifty.doesUserHavePosting(userId)
    if hasPosting:
        await ctx.channel.send(name + ', you already have a posting. Do "!50remove" to cancel it.')
        return

    #Try to create the posting
    success = botFifty.createPosting(userId, name, amount)
    if success == False:
        await ctx.channel.send(name + ', you already have a posting. Do "!50remove" to cancel it.')
        return

    #Take the money from the user
    botBank.updateBalance(userId, -amount)

    await ctx.channel.send(name + ', you have created a 50/50 posting for ' + str(helper.moneyFormat(amount)))


#===============================================
#   50see - Checks all 50/50 postings available
#===============================================
@bot.command(name='50see', aliases=['fs'], help='Shows all available 50/50 postings',  ignore_extra=True) 
async def fiftySee(ctx):
    await ctx.channel.send(botFifty.displayPostings())


#===============================================
#   50accept - Accepts a 50/50 posting
#===============================================
@bot.command(name='50accept', aliases=['fa'], help='[name]', brief='[name] - Accepts and starts a 50/50 game',  ignore_extra=True) 
async def fiftyCreate(ctx, displayName : str):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    #Checks to make sure the given name actually has a posting
    postingAmount = botFifty.getPostingAmountIfExists(displayName)
    if postingAmount == -1:
        await ctx.channel.send(name + ', there is no posting by the username you supplied')
        return

    #Checks for any errors of the input
    resultMsg = validation(userId, postingAmount)

    if resultMsg != '':
        await ctx.channel.send(resultMsg)
        return

    #Flip a coin and store the result (0 = poster, 1 = challenger)
    result = choice([0, 1])

    #Get the user id of the poster
    posterId = botFifty.getPostingUserIdIfExists(displayName)
    if posterId == '':
        await ctx.channel.send(name + ', there is no posting by the username you supplied')
        return

    #Remove the posting
    botFifty.removePosting(posterId)

    if result == 0: #Poster won
        await processFiftyFifty(ctx, userId, displayName, -1, postingAmount, False)
        await processFiftyFifty(ctx, posterId, name, 1, postingAmount, True)
    else: #Challenger won
        await processFiftyFifty(ctx, userId, displayName, 1, postingAmount, False)
        await processFiftyFifty(ctx, posterId, name, -1, postingAmount, True)


#===============================================
#   50remove - Cancels your own 50/50 posting
#===============================================
@bot.command(name='50remove', aliases=['fr'], help='Removes your own 50/50 posting',  ignore_extra=True) 
async def fiftyRemove(ctx):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    #Check if there is already a posting for this user
    hasPosting = botFifty.doesUserHavePosting(userId)
    if hasPosting:
        #Give the money back to the user
        botBank.updateBalance(userId, botFifty.getPostingAmountIfExists(name))

        #Remove the posting
        botFifty.removePosting(userId)

        await ctx.channel.send(name + ', your 50/50 posting has been removed successfully.')
    else:
        await ctx.channel.send(name + ', you do not have a posting to remove')


#===============================================
#   LOAN
#===============================================
@bot.command(name='loan', aliases=["l"], help=f'The bank will loan you every {loaner.secondsToWait} seconds', ignore_extra=True, case_insensitive=False) 
async def getLoan(ctx):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    #Get the loan amount the bank offers - if no loan is allowed, it will be negative
    loanAmount = botLoaner.askForLoan(userId)

    if loanAmount < 0:
        timeLeft = botLoaner.checkTimeLeftBeforeLoan(userId)
        await ctx.channel.send(timeLeft)
    else:
        botBank.updateBalance(userId, loanAmount, False)
        botBank.updatePlayerStat(userId, 'loans', 1)
        await ctx.channel.send(name + ', you have been loaned: ' + str(helper.moneyFormat(loanAmount)))


#===============================================
#   BALANCE
#===============================================
@bot.command(name='balance', aliases=["bal","b"], help='(optional: name) Shows the balance of yourself or another', ignore_extra=True) 
async def checkBalance(ctx, name = ''):
    userId = ctx.author.id
    outputText = 'Your balance is: '

    if name != '':
        userId = await getIdFromDisplayName(ctx, name)

        if userId == -1:
            await ctx.channel.send('No one in the discord has a display name that matches what you supplied')
            return

        outputText = 'Their balance is: '

    #Create new balance if user doesn't exist yet
    botBank.createNewUserStats(userId)

    balance = helper.moneyFormat(botBank.balances[str(userId)]['balance'])

    await ctx.channel.send(outputText + str(balance))


#===============================================
#   STATS
#===============================================
@bot.command(name='stats', aliases=["st"], help='(optional: name) Shows the stats of yourself or another', ignore_extra=True) 
async def checkStats(ctx, name = ''):
    userId = ctx.author.id
    displayName = name.capitalize()

    if displayName != '':
        userId = await getIdFromDisplayName(ctx, displayName)

        if userId == -1:
            await ctx.channel.send('No one in the discord has a display name that matches what you supplied')
            return
    else:
        displayName = ctx.author.display_name

    #Get the stats of the player with the specified id
    await ctx.channel.send(botBank.getPlayerStats(userId, displayName))


#===============================================
#   GLOBAL STATS
#===============================================
@bot.command(name='globalStats', aliases=["gs"], help='Shows the stats of everyone in the channel', ignore_extra=True) 
async def checkGlobalStats(ctx):
    
    #Get the stats of everyone in the channel
    await ctx.channel.send(botBank.getGlobalStats())


#===============================================
#   TRINKET NEXT
#===============================================
@bot.command(name='trinketNext', aliases=["tn"], help='Shows the next trinket you can buy', ignore_extra=True) 
async def trinketNext(ctx):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    #Get the players current level
    level = botTrinkets.getTrinketLevel(userId, botBank.balances)

    #Check to see if they are at the maximum amount of trinkets
    if level == botTrinkets.getMaxTrinketLevel():
        await ctx.channel.send(name + ', you already have the maximum amount of trinkets (' + str(level) + ')')
        return

    if level == -1:
        await ctx.channel.send(name + ', you do not have a trinkets value. Contact an administrator')

    #Get the price of the next level trinket
    price = botTrinkets.getNextTrinketPrice(userId, botBank.balances)

    await ctx.channel.send(name + ', you have ' + str(level) + ' trinkets. The next one costs ' + str(helper.moneyFormat(round(price))))


#===============================================
#   TRINKET CHECK
#===============================================
@bot.command(name='trinketCheck', aliases=["tc"], help='Shows current bonuses from your trinkets', ignore_extra=True) 
async def trinketCheck(ctx):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    #Get the bonus based on the current level
    bonus = botTrinkets.getBonusFromTrinkets(userId, botBank.balances)

    await ctx.channel.send(name + ', you have an additional ' + str(round(100 * bonus)) + '% chance to win in games against the House')


#===============================================
#   TRINKET BUY
#===============================================
@bot.command(name='trinketBuy', aliases=["tb"], help='Buys the next available trinket', ignore_extra=True) 
async def trinketBuy(ctx):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    #Get the new level
    level = botTrinkets.getTrinketLevel(userId, botBank.balances)

    #Check to see if they are at the maximum amount of trinkets
    if level == botTrinkets.getMaxTrinketLevel():
        await ctx.channel.send(name + ', you already have the maximum amount of trinkets (' + str(level) + ')')
        return

    #Get the price of the next trinket
    price = botTrinkets.getNextTrinketPrice(userId, botBank.balances)

    #Checks for any errors of the input
    resultMsg = validation(userId, price)

    if resultMsg != '':
        await ctx.channel.send(resultMsg)
        return

    #Increment the trinket level of the user
    botTrinkets.incrementTrinketAmount(userId, botBank.balances)

    #Get the new level
    level = botTrinkets.getTrinketLevel(userId, botBank.balances)

    #Update the balance of the user
    botBank.updateBalance(userId, -price, False)

    await ctx.channel.send(name + ', you bought trinket ' + str(level) + ' for ' + str(helper.moneyFormat(price)))


#===============================================
#   TRINKET TOP
#===============================================
@bot.command(name='trinketTop', aliases=["tt"], help='Shows who has the most trinkets', ignore_extra=True) 
async def trinketTop(ctx):
    userId = ctx.author.id

    #Get the latest member list
    members = []
    async for member in ctx.guild.fetch_members(limit=None):
        members.append((member.id,member.display_name))
    
    #Create the leaderboard string
    message = botTrinkets.getTopTrinkets(userId, members, botBank.balances)

    await ctx.channel.send(message)


#===============================================
#   GOONS CLAIM
#===============================================
@bot.command(name='goonsClaim', aliases=["gc"], help='Claims all offline income from your goons', ignore_extra=True) 
async def goonsClaim(ctx):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    timeSinceClaimed = botGoons.getTimeSinceClaimed(userId)
    claimedAmount = botGoons.claimGoonIncome(userId, botBank.balances)

    #Check to see if the player has no Goons
    if claimedAmount == -1 or timeSinceClaimed == -1:
        await ctx.channel.send(name + ', you do not have any Goons under your command')
        return

    #Check to see if the Goons haven't made enough money to warrant any giveaway
    if claimedAmount == 0:
        await ctx.channel.send(name + ', your Goons have not made any money since you last checked')
        return

    formattedTime = helper.formatTime(timeSinceClaimed)

    #Update the balance of the user
    botBank.updateBalance(userId, claimedAmount, False)

    await ctx.channel.send(name + ', after ' + formattedTime + ', your goons have earned you a total of ' + str(helper.moneyFormat(claimedAmount)))


#===============================================
#   GOONS NEXT
#===============================================
@bot.command(name='goonsNext', aliases=["gn"], help='Shows the next goon you can buy', ignore_extra=True) 
async def goonsNext(ctx):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    #Get the players next available goon purchase
    goonNumber, price  = botGoons.getNextAvailableGoon(userId, botBank.balances)

    #Check to see if they are at the maximum amount of trinkets
    if price == -1:
        await ctx.channel.send(name + ', you have already purchased all available goons')
        return

    await ctx.channel.send(name + ', the next Goon (#' + str(goonNumber) + ') you can purchase will cost ' + str(helper.moneyFormat(price)))


#===============================================
#   GOONS BUY
#===============================================
@bot.command(name='goonsBuy', aliases=["gb"], help='Buys the next available goon', ignore_extra=True) 
async def goonsBuy(ctx):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    #Get the players next available goon purchase
    goonNumber, price  = botGoons.getNextAvailableGoon(userId, botBank.balances)

    #Check to see if they are at the maximum amount of trinkets
    if price == -1:
        await ctx.channel.send(name + ', you have already purchased all available goons')
        return

    #Checks for any errors of the input
    resultMsg = validation(userId, price)

    if resultMsg != '':
        await ctx.channel.send(resultMsg)
        return

    #Increment the trinket level of the user
    botGoons.incrementGoonAmount(userId, botBank.balances, goonNumber)

    #Update the balance of the user
    botBank.updateBalance(userId, -price, False)

    await ctx.channel.send(name + ', Goon ' + str(goonNumber) + ' will now start making cash for you on the side. The Goon cost you ' + str(helper.moneyFormat(price)))


#===============================================
#   GOONS INFO
#===============================================
@bot.command(name='goonsInfo', aliases=["gi"], help='Shows all goon info and upgrade costs') 
async def goonsInfo(ctx):
    userId = ctx.author.id

    output = botGoons.getGoonLevelStats(botBank.balances[str(userId)])

    await ctx.channel.send(output)


#===============================================
#   GOONS UPGRADE CHECK
#===============================================
@bot.command(name='goonsUpgradeCheck', aliases=["guc"], help='[goon #]', brief='[goon #] - Shows upgrade cost of the specified goon', ignore_extra=True) 
async def goonsUpgradeCheck(ctx, goonNumber : int):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    numOfGoons = len(goons.goonSetup)

    #Validate the input parameter is correct
    if(goonNumber <= 0 or goonNumber > numOfGoons):
        await ctx.channel.send(name + ', you must supply a Goon number between 1 and ' + str(numOfGoons))
        return

    goonLevels = botGoons.getGoonLevels(botBank.balances[str(userId)])

    #Check to see if they even have the specified Goon purchased
    if goonLevels[goonNumber] == 0:
        await ctx.channel.send(name + ', you do not have that Goon purchased yet')
        return

    nextGoon,price = botGoons.getNextAvailableGoon(userId, botBank.balances)

    if nextGoon != -1 and goonNumber > nextGoon:
        await ctx.channel.send(name + ', you do not have that Goon purchased yet. You are currently on Goon ' + str(nextGoon-1))
        return 

    price = botGoons.getGoonUpgradePrice(userId, botBank.balances, goonNumber)
    
    if price == -1:
        await ctx.channel.send(name + ', that Goon is at the maximum level')
        return 

    await ctx.channel.send(name + ', to upgrade Goon ' + str(goonNumber) + ' it will cost ' + str(helper.moneyFormat(price)))


#===============================================
#   GOONS UPGRADE
#===============================================
@bot.command(name='goonsUpgrade', aliases=["gu"], help='[goon #]', brief='[goon #] - Upgrades the specified goon', ignore_extra=True) 
async def goonsUpgrade(ctx, goonNumber : int):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    numOfGoons = len(goons.goonSetup)

    #Validate the input parameter is correct
    if(goonNumber <= 0 or goonNumber > numOfGoons):
        await ctx.channel.send(name + ', you must supply a Goon number between 1 and ' + str(numOfGoons))
        return

    goonLevels = botGoons.getGoonLevels(botBank.balances[str(userId)])

    #Check to see if they even have the specified Goon purchased
    if goonLevels[goonNumber] == 0:
        await ctx.channel.send(name + ', you do not have that Goon purchased yet')
        return

    nextGoon,price = botGoons.getNextAvailableGoon(userId, botBank.balances)

    if nextGoon != -1 and goonNumber > nextGoon:
        await ctx.channel.send(name + ', you do not have that Goon purchased yet. You are currently on Goon ' + str(nextGoon-1))
        return 

    price = botGoons.getGoonUpgradePrice(userId, botBank.balances, goonNumber)
    
    if price == -1:
        await ctx.channel.send(name + ', that Goon is at the maximum level')
        return 

    #Checks for any errors of the input
    resultMsg = validation(userId, price)

    if resultMsg != '':
        await ctx.channel.send(resultMsg)
        return

    #Increment the trinket level of the user
    botGoons.incrementGoonAmount(userId, botBank.balances, goonNumber)

    #Update the balance of the user
    botBank.updateBalance(userId, -price, False)

    await ctx.channel.send(name + ', you upgraded Goon ' + str(goonNumber) + ', costing ' + str(helper.moneyFormat(price)))


#===============================================
#   GOONS TOP
#===============================================
@bot.command(name='goonsTop', aliases=["gt"], help='[goon #]', brief='[goon #] - Shows the top levels of a goon', ignore_extra=True) 
async def goonsTop(ctx, goonNumber : int):
    userId = ctx.author.id

    #Get the latest member list
    members = []
    async for member in ctx.guild.fetch_members(limit=None):
        members.append((member.id,member.display_name))
    
    #Create the leaderboard string
    message = botGoons.getTopGoonLevels(userId, members, botBank.balances, goonNumber)

    await ctx.channel.send(message)


#===============================================
#   LEADERBOARD
#===============================================
@bot.command(name='ranking', aliases=["rank","ra"], help='Ranks users based on their balance', ignore_extra=True) 
async def ranking(ctx):
    userId = ctx.author.id

    #Get the latest member list
    members = []
    async for member in ctx.guild.fetch_members(limit=None):
        members.append((member.id,member.display_name))
    
    #Create the leaderboard string
    message = botBank.getTopBalances(userId, members)

    await ctx.channel.send(message)



#===============================================
#
#   ADMIN COMMANDS - When a new one is added, 
#                    add it to the list below
#
#===============================================



#===============================================
#   ADMIN
#===============================================
@bot.command(name='admin', help='Shows admin commands', ignore_extra=True) 
@commands.has_permissions(administrator=True)
async def checkAdmin(ctx):
    adminCommands = ['mod','reset']
    output = '===== ADMIN COMMANDS =====\n'

    for i in adminCommands:
        cmd = bot.get_command(i)
        output += '• ' + cmd.name + ' - ' + cmd.help + '\n'

    await ctx.author.send(output)


#===============================================
#   MOD
#===============================================
@bot.command(name='mod', hidden=True, help='[displayName] [amount] - Modifies a players balance') 
@commands.has_permissions(administrator=True)
async def modifyBalance(ctx, displayName : str, amount : int):
    userId = await getIdFromDisplayName(ctx, displayName)
    
    if userId == -1:
        await ctx.author.send('No one in the discord has a display name that matches what you supplied to the add command')
    else:
        botBank.updateBalance(userId, amount, False)

    print(str(userId) + ' : ' + displayName.capitalize() + ' has been given ' + str(amount) + ' by the bank! How lucky!')
    await ctx.channel.send(displayName.capitalize() + ' has been given ' + str(amount) + ' by the bank! How lucky!')


#===============================================
#   RESET STATS
#===============================================
@bot.command(name='reset', hidden=True, help='[displayName] - Resets a players stats') 
@commands.has_permissions(administrator=True)
async def resetPlayerStats(ctx, displayName : str):
    userId = await getIdFromDisplayName(ctx, displayName)
    
    if userId == -1:
        await ctx.author.send('No one in the discord has a display name that matches what you supplied to the add command')
    else:
        botBank.resetPlayerStats(userId)

    await ctx.channel.send(displayName.capitalize() + ' has had their stats reset')



#===============================================
#
#   GAMES EMBED COMMANDS 
#   - Adds an embed and allows players to join games
#       by reacting to the emojis on the embed
#
#===============================================



#===============================================
#   GAMES
#===============================================
@bot.command(name='games', help='Creates the embed and adds the initial reactions',  hidden=True, ignore_extra=True) 
@commands.has_permissions(administrator=True)
async def showGameEmbed(ctx):
    messageId = botGameEmbed.getGameMessageId()

    #Check if a games message already exists and if so delete it
    if messageId != -1:
        messageToDelete = await ctx.channel.fetch_message(messageId)
        await messageToDelete.delete()

    #Delete the command message
    await ctx.message.delete()

    message = await ctx.channel.send(embed = getGameEmbed())
    botGameEmbed.setGameMessageId(message.id)

    #Add all of the emojis as reactions to the message
    for emoji in botGameEmbed.getEmojisInUse():
        await message.add_reaction(emoji = emoji)


@bot.command(name='gameAdd', help='[emoji] [game name] [slots] Adds the given emoji/game line',  hidden=True, ignore_extra=True) 
@commands.has_permissions(administrator=True)
async def addGameToGameEmbed(ctx, emoji : str, gameName : str, slots : int):
    messageId = botGameEmbed.getGameMessageId()

    #Delete the command message
    await ctx.message.delete()

    #Add the game to the list
    botGameEmbed.addGame(gameName, emoji, slots)

    #Add the new emoji as a reaction to the message - if exists
    if messageId != -1:
        message = await ctx.channel.fetch_message(messageId)
        await message.edit(embed = getGameEmbed())
        await message.add_reaction(emoji = emoji)


@bot.command(name='gameRemove', help='[game name] Removes the Adds the given emoji/game line', hidden=True, ignore_extra=True) 
@commands.has_permissions(administrator=True)
async def removeGameFromGameEmbed(ctx, gameName : str):
    messageId = botGameEmbed.getGameMessageId()

    #Delete the command message
    await ctx.message.delete()

    #Get the emoji used by the game
    emoji = botGameEmbed.getEmojiGivenName(gameName)

    #Remove the game from the list
    botGameEmbed.removeGameByName(gameName)

    #Remove the emoji as a reaction to the message - if exists
    if messageId != -1 and emoji != -1:
        message = await ctx.channel.fetch_message(messageId)
        await message.edit(embed = getGameEmbed())
        await message.clear_reaction(emoji)
    

@bot.event
async def on_reaction_add(reaction, member):
    emoji = reaction.emoji
    message = reaction.message

    messageId = botGameEmbed.getGameMessageId()

    #If the bot reacts or the "games" message isnt setup yet return
    if member.bot or messageId == -1:
        return

    #If the reaction was on a message other than the "games" message ignore it
    if message.id != messageId:
        return

    #If the emoji reacted with is not part of the games list options remove it
    if emoji not in botGameEmbed.getEmojisInUse():
        await message.clear_reaction(emoji)

    userId = member.id
    displayName = str(member.display_name)

    botGameEmbed.addPlayerToGame(emoji, userId, displayName)

    await message.edit(embed = getGameEmbed())

    #How to remove a reaction completely from a message
    #await message.remove_reaction(emoji, member)


@bot.event
async def on_reaction_remove(reaction, member):
    emoji = reaction.emoji
    message = reaction.message

    messageId = botGameEmbed.getGameMessageId()

    #If the bot reacts or the "games" message isnt setup yet return
    if member.bot or messageId == -1:
        return

    #If the reaction was on a message other than the "games" message ignore it
    if message.id != messageId:
        return

    userId = member.id

    botGameEmbed.removePlayerFromGame(emoji, userId)

    await message.edit(embed = getGameEmbed())

    #Remove the players reaction from the message
    await message.remove_reaction(emoji, member)


def getGameEmbed():
    embed = discord.Embed(color=0x42413e)
    embed.add_field(name=':raised_hands: The squad awaits you! :raised_hands: Join up! :fist:', value=botGameEmbed.getEmbedMessage(), inline=True)

    return embed


#Start the bot
bot.run(TOKEN)