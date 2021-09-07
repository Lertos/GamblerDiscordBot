import json

gameListFile = 'gameEmbed.json'
emptySlotChar = '?'


class GameEmbed:
    def __init__(self):
        self.addedGames = []
        self.loadAddedGames()

        self.gamesMessageId = -1


    #Reads the json file containing all added games
    def loadAddedGames(self):
        with open(gameListFile) as f:
            games = json.load(f)

            for i in range(0, len(games)):
                index = str(i)
                game = games[index]['game']
                emoji = games[index]['emoji']
                members = games[index]['members']
            
                self.addedGames.append((game, emoji, members))


    #Saves the json file with the updated game list
    def saveAddedGames(self):
        games = {}

        for i in range(0, len(self.addedGames)):
            game,emoji,members = self.addedGames[i]

            games[i] = {}
            games[i]['game'] = game
            games[i]['emoji'] = emoji
            games[i]['members'] = []
            
            if len(members) != 0:
                for j in range(0, len(members)):
                    games[i]['members'].append(members[j])

        with open(gameListFile,'w') as f:
            f.write(json.dumps(games))


    def getEmbedMessage(self):
        output = ''

        for i in range(0, len(self.addedGames)):
            output += str(self.addedGames[i][1]) + ' : **' + self.addedGames[i][0] + '**'
            memberList = '  - [ '

            for j in range(0, len(self.addedGames[i][2])):
                memberList += str(self.addedGames[i][2][j][1]) + ', '
            
            #Remove ending comma
            if memberList != '  - [ ':
                memberList = memberList[0:-2] + ' ]\n'
            else:
                memberList = '\n'
            output += memberList

        return output


    def getAddedGames(self):
        return self.addedGames


    def addGame(self, name, emoji, slots):
        members = []
        for i in range(0,slots):
            members.append((emptySlotChar, emptySlotChar))

        self.addedGames.append((name, emoji, members))
        self.saveAddedGames()


    #Removes the tuple of the game specified by the given name
    def removeGameByName(self, name):
        index = self.getIndexByGameName(name)
        
        if index != -1:
            self.addedGames.pop(index)
            self.saveAddedGames()


    def getEmojisInUse(self):
        emojis = []

        for i in range(0, len(self.addedGames)):
            emojis.append(self.addedGames[i][1])

        return emojis


    def getEmojiGivenName(self, name):
        for i in range(0, len(self.addedGames)):
            if self.addedGames[i][0].lower() == name.lower():
                return self.addedGames[i][1]
        return -1
            

    #Returns the index of the game given a name
    def getIndexByGameName(self, name):
        for i in range(0, len(self.addedGames)):
            gameName = self.addedGames[i][0]

            if gameName.lower() == name.lower():
                return i
        #No game was found with the given name
        return -1


    #Returns the index of the game given an emoji
    def getIndexByEmojiName(self, emoji):
        for i in range(0, len(self.addedGames)):
            emojiName = self.addedGames[i][1]

            if emojiName == emoji:
                return i
        #No game was found with the given emoji
        return -1


    #Returns the game name given an emoji
    def getGameNameByEmojiName(self, emoji):
        for i in range(0, len(self.addedGames)):
            if self.addedGames[i][1] == emoji:
                return self.addedGames[i][0]
        #No game was found with the given emoji
        return -1


    #Adds a player to the list of members for a game, given an emoji
    def addPlayerToGame(self, emoji, userId, displayName):
        index = self.getIndexByEmojiName(emoji)
        
        if index != -1:
            id = str(userId)
            members = self.addedGames[index][2]

            #If the user already exists just return
            for i in range(0, len(members)):
                if id == members[i][0]:
                    return
            
            #Check for an available slot and then replace it with the new player
            for i in range(0, len(members)):
                if members[i][0] == emptySlotChar:
                    self.addedGames[index][2][i] = (id, displayName)
                    self.saveAddedGames()
                    return


    #Adds a player to the list of members for a game, given an emoji
    def removePlayerFromGame(self, emoji, userId):
        index = self.getIndexByEmojiName(emoji)
        
        if index != -1:
            id = str(userId)
            members = self.addedGames[index][2]

            for i in range(0, len(members)):
                if id == members[i][0]:
                    self.addedGames[index][2][i] = (emptySlotChar, emptySlotChar)
                    self.saveAddedGames()
                    return


    def getGameMessageId(self):
        return self.gamesMessageId


    def setGameMessageId(self, messageId):
        self.gamesMessageId = messageId