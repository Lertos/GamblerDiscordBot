import os
import discord
import bank
import helper
import fifty
from discord.flags import Intents
import loaner
from random import randrange, choice
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

#Setup variables
flipPayoutRate = 1
rollPayoutRate = 6
blackjackPayoutRate = 1

#===============================================
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
#   Check to make sure the user has a balance
#   If not, add them to the bank
#===============================================
def createUserBalanceIfNeeded(userId):
    if str(userId) not in botBank.balances:
        botBank.createNewBalance(userId)


#===============================================
#   Validation checks for any type of betting
#===============================================
def validation(userId, amount):
    resultMsg = ''

    #Create new balance if user doesn't exist yet
    createUserBalanceIfNeeded(userId)

    #Check to make sure the amount is positive
    if amount <= 0:
        resultMsg = 'The betting amount must be over 0$'

    #Check to make sure the user has enough money
    elif botBank.balances[str(userId)]['balance'] < amount:
        resultMsg = 'You do not have enough money to bet that high'

    return resultMsg


#===============================================
#   Gets the payout based on if the guess was correct
#===============================================
def getPayoutResult(userId, amount, multiplier, result, guess):
    #Calculate the payout to the user
    if result == guess:
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
#   FLIP
#===============================================
@bot.command(name='flip', aliases=["f"], help='[h | t] [bet amount]', brief='[h | t] [bet amount] - Flips a coin (1/2 chance, 2 * payout)',  ignore_extra=True) 
async def flipCoin(ctx, guess : str, amount : int):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    #Check to make sure the player supplied either a 'h' or a 't'
    if guess != 'h' and guess != 't':
        await ctx.channel.send(name + ', you must supply either ''h'' (heads) or ''t'' (tails)')
        return

    #Checks for any errors of the input
    resultMsg = validation(userId, amount)

    if resultMsg != '':
        await ctx.channel.send(resultMsg)
        return

    #Flip the coin and store the result
    result = choice(['h', 't'])

    payout = getPayoutResult(userId, amount, flipPayoutRate, result, guess)

    #Send the user the message of the payout and whether they won
    if payout < 0:
        botBank.updatePlayerStats(userId, 'flip', -1)
        await ctx.channel.send(':regional_indicator_' + result + ':  ' + name + ', you **LOST**... **' + str(helper.moneyFormat(abs(payout))) + '** has been removed from your balance')
    else:
        botBank.updatePlayerStats(userId, 'flip', 1)
        await ctx.channel.send(':regional_indicator_' + result + ':  ' + name + ', you **WON**! **' + str(helper.moneyFormat(abs(payout))) + '** has been added to your balance')


#===============================================
#   ROLL
#===============================================
@bot.command(name='roll', aliases=["ro"], help='[1 - 6] [bet amount]', brief='[1-6] [bet amount] Rolls a dice (1/6 chance, 6 * payout)', ignore_extra=True) 
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

    #Roll the dice and store the result
    result = randrange(1, 7)

    payout = getPayoutResult(userId, amount, rollPayoutRate, result, guess)

    #Send the user the message of the payout and whether they won
    if payout < 0:
        botBank.updatePlayerStats(userId, 'roll', -1)
        await ctx.channel.send(helper.getRollNumberWord(result) + '  ' + name + ', you guessed ' + str(guess) + ' and **LOST**... **' + str(helper.moneyFormat(abs(payout))) + '** has been removed from your balance')
    else:
        botBank.updatePlayerStats(userId, 'roll', 1)
        await ctx.channel.send(helper.getRollNumberWord(result) + '  ' + name + ', you guessed ' + str(guess) + ' and **WON**! **' + str(helper.moneyFormat(abs(payout))) + '** has been added to your balance')


#===============================================
#   50start - Creates a new 50/50 posting
#===============================================
@bot.command(name='50start', aliases=["fs"], help='[bet amount]', brief='[bet amount] - Creates a new 50/50 posting',  ignore_extra=True) 
async def fiftyStart(ctx, amount : int):
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
        await ctx.channel.send(name + ', you already have a posting. Do "!50cancel" to cancel it.')
        return

    success = botFifty.createPosting(userId, name, amount)
    if success == False:
        await ctx.channel.send(name + ', you already have a posting. Do "!50cancel" to cancel it.')
        return

    await ctx.channel.send(name + ', you have created a 50/50 posting for ' + str(helper.moneyFormat(amount)) + '$')


#===============================================
#   50check - Checks all 50/50 postings available
#===============================================
@bot.command(name='50check', aliases=["fc"], help='Shows all available 50/50 postings',  ignore_extra=True) 
async def fiftyCheck(ctx):
    await ctx.channel.send(botFifty.displayPostings())


#===============================================
#   50accept - Accepts a 50/50 posting
#===============================================


#===============================================
#   50cancel - Cancels your own 50/50 posting
#===============================================


#===============================================
#   21
#===============================================


#===============================================
#   LOAN
#===============================================
@bot.command(name='loan', aliases=["lo"], help=f'The bank will loan you every {loaner.secondsToWait} seconds', ignore_extra=True, case_insensitive=False) 
async def getLoan(ctx):
    userId = ctx.author.id
    name = str(ctx.author.display_name)

    #Get the loan amount the bank offers - if no loan is allowed, it will be negative
    loanAmount = botLoaner.askForLoan(userId)

    if loanAmount < 0:
        timeLeft = botLoaner.checkTimeLeft(userId)
        await ctx.channel.send(timeLeft)
    else:
        botBank.updateBalance(userId, loanAmount)
        botBank.updateLoanStat(userId)
        await ctx.channel.send(name + ', you have been loaned: ' + str(helper.moneyFormat(loanAmount)))


#===============================================
#   BALANCE
#===============================================
@bot.command(name='balance', aliases=["bal"], help='(optional: name) Shows the balance of yourself or another', ignore_extra=True) 
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
    createUserBalanceIfNeeded(userId)

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
    message = botBank.getLeaderboard(userId, members)

    await ctx.channel.send(message)


#===============================================
#
#   ADMIN COMMANDS
#
#===============================================

#===============================================
#   ADMIN
#===============================================
@bot.command(name='admin', help='Shows admin commands', ignore_extra=True) 
@commands.has_permissions(administrator=True)
async def checkAdmin(ctx):
    adminCommands = ['mod']
    output = '===== ADMIN COMMANDS =====\n'

    for i in adminCommands:
        cmd = bot.get_command(i)
        output += '• ' + cmd.name + ' - ' + cmd.help + '\n'

    await ctx.author.send(output)


#===============================================
#   MOD
#===============================================
@bot.command(name='mod', hidden=True, help='[displayName] [amount] [hide] - Modifies a players balance') 
@commands.has_permissions(administrator=True)
async def modifyBalance(ctx, displayName : str, amount : int, hide = 0):
    if hide not in [0,1]:
        await ctx.author.send('Unless [hide] is 1 (to hide the output) it is not needed')
    
    userId = await getIdFromDisplayName(ctx, displayName)
    
    if userId == -1:
        await ctx.author.send('No one in the discord has a display name that matches what you supplied to the add command')
    else:
        botBank.updateBalance(userId, amount)

        if hide == 0:
            await ctx.channel.send(displayName.capitalize() + ' has been given ' + str(amount) + ' by the bank! How lucky!')


#Start the bot
bot.run(TOKEN)