import os
import discord
from random import randrange, choice
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

#Setup variables
flipPayoutRate = 2
rollPayoutRate = 6
blackjackPayoutRate = 2

#===============================================
#   ON READY
#===============================================
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    #members = '\n - '.join([member.name for member in bot.guilds[0].members])


#===============================================
#   FLIP
#===============================================
@bot.command(name='flip', help='[h/t] [bet amount] - Flips a coin (1/2 chance, 2 * payout)') 
async def user_msg(ctx, guess : str, amount : int):
    #Check to make sure the player supplied either a 'h' or a 't'
    if guess != 'h' and guess != 't':
        await ctx.channel.send('You must supply either ''h'' (heads) or ''t'' (tails)')
        return

    #Check to make sure the user has enough money
    #TODO

    #Flip the coin and store the result
    side = choice(['h', 't'])

    #Check if the player won the coin flip
    userWon = -1

    if side == guess:
        userWon = 1
    
    #Calculate the payout to the user
    payout = amount * flipPayoutRate * userWon

    #Add the payout to the users balance
    #TODO

    #Send the user the message of the payout and whether they won
    if userWon == -1:
        await ctx.channel.send('You LOST... ' + str(payout) + ' has been removed from your balance')
    else:
        await ctx.channel.send('You WON! ' + str(payout) + ' has been added to your balance')


#===============================================
#   ROLL
#===============================================
@bot.command(name='roll', help='[1-6] [bet amount] Rolls a dice (1/6 chance, 6 * payout)') 
async def roll_dice(ctx, guess : int, amount : int):
    #Check to make sure the player supplied either a valid die side
    if guess < 1 or guess > 6:
        await ctx.channel.send('You must supply a number between 1-6')
        return

    #Check to make sure the user has enough money
    #TODO

    #Roll the die and store the result
    roll = randrange(1, 7)

    #Check if the player won the roll
    userWon = -1

    if roll == guess:
        userWon = 1
    
    #Calculate the payout to the user
    payout = amount * rollPayoutRate * userWon

    #Add the payout to the users balance
    #TODO

    #Send the user the message of the payout and whether they won
    if userWon == -1:
        await ctx.channel.send('Rolled: [' + roll + ']. You guessed ' + str(guess) + ' and LOST... ' + str(payout) + ' has been removed from your balance')
    else:
        await ctx.channel.send('Rolled: [' + roll + ']. You guessed ' + str(guess) + ' and WON! ' + str(payout) + ' has been added to your balance')


#===============================================
#   ROLL
#===============================================


#===============================================
#   ROLL
#===============================================


#===============================================
#   ROLL
#===============================================


#===============================================
#   ROLL
#===============================================


#Start the bot
bot.run(TOKEN)