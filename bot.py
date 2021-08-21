import os
import discord
import bank
from random import randrange, choice
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')
botBank = bank.Bank()

#Setup variables
flipPayoutRate = 1
rollPayoutRate = 6
blackjackPayoutRate = 1

#===============================================
#   ON READY
#===============================================
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(botBank.balances)
    #members = '\n - '.join([member.name for member in bot.guilds[0].members])


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
    elif botBank.balances[str(userId)] < amount:
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
#   FLIP
#===============================================
@bot.command(name='flip', help='[h/t] [bet amount] - Flips a coin (1/2 chance, 2 * payout)') 
async def flipCoin(ctx, guess : str, amount : int):
    #Check to make sure the player supplied either a 'h' or a 't'
    if guess != 'h' and guess != 't':
        await ctx.channel.send('You must supply either ''h'' (heads) or ''t'' (tails)')
        return

    userId = ctx.author.id

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
        await ctx.channel.send('You LOST... ' + str(abs(payout)) + ' has been removed from your balance')
    else:
        await ctx.channel.send('You WON! ' + str(abs(payout)) + ' has been added to your balance')


#===============================================
#   ROLL
#===============================================
@bot.command(name='roll', help='[1-6] [bet amount] Rolls a dice (1/6 chance, 6 * payout)') 
async def rollDice(ctx, guess : int, amount : int):
    #Check to make sure the player supplied either a valid die side
    if guess < 1 or guess > 6:
        await ctx.channel.send('You must supply a number between 1-6')
        return

    userId = ctx.author.id

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
        await ctx.channel.send('Rolled: [' + str(result) + ']. You guessed ' + str(guess) + ' and LOST... ' + str(abs(payout)) + ' has been removed from your balance')
    else:
        await ctx.channel.send('Rolled: [' + str(result) + ']. You guessed ' + str(guess) + ' and WON! ' + str(abs(payout)) + ' has been added to your balance')


#===============================================
#   ROLL
#===============================================


#===============================================
#   ROLL
#===============================================


#===============================================
#   BALANCE
#===============================================
@bot.command(name='balance', help='Checks your balance or sets it up for you') 
async def checkBalance(ctx):
    userId = ctx.author.id

    #Create new balance if user doesn't exist yet
    createUserBalanceIfNeeded(userId)

    await ctx.channel.send('Your balance is: ' + str(botBank.balances[str(userId)]))


#Start the bot
bot.run(TOKEN)