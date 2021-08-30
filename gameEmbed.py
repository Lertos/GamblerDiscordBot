

class GameEmbed:
    def __init__(self):
        self.emojisInUse = []
        self.gamesMessageId = -1


    def getEmojisInUse(self):
        return self.emojisInUse


    def addEmojisInUse(self, emoji):
        self.emojisInUse.append(emoji)


    def removeEmojisInUse(self, emoji):
        self.emojisInUse.remove(emoji)


    def getGameMessageId(self):
        return self.gamesMessageId


    def setGameMessageId(self, messageId):
        self.gamesMessageId = messageId