import json
import helper

postingFile = 'postings.json'


class FiftyFifty:
    def __init__(self):
        self.postings = self.loadPostings(postingFile)


    #Reads the json file containing all postings
    def loadPostings(self, fileName):
        with open(fileName) as f:
            return json.load(f)


    #Saves the json file with the updated postings
    def savePostings(self):
        with open(postingFile,'w') as f:
            f.write(json.dumps(self.postings))


    #Returns a bool whether or not the user has a posting or not
    def doesUserHavePosting(self, userId):
        id = str(userId)

        if id in self.postings.keys():
            return True
        return False


    #Returns -1 if the posting doesnt exist or the amount in the posting if it does exist
    def getPostingAmountIfExists(self, name):
        for key in self.postings.keys():
            if self.postings[key]['name'].lower() == name.lower():
                return self.postings[key]['amount']
        return -1


    #Returns the user id of a posting based on the name
    def getPostingUserIdIfExists(self, name):
        for key in self.postings.keys():
            if self.postings[key]['name'].lower() == name.lower():
                return str(key)
        return ''


    #Create posting with the given amount
    def createPosting(self, userId, name, amount):
        id = str(userId)

        if id in self.postings.keys():
            return False
        
        self.postings[id] = {}

        self.postings[id]['name'] = name
        self.postings[id]['amount'] = amount

        self.savePostings()

        return True


    #Remove a posting based on given user id
    def removePosting(self, userId):
        id = str(userId)

        if id in self.postings.keys():
            self.postings.pop(id, None)

        self.savePostings()


    #Returns a string with all the postings
    def displayPostings(self):
        output = helper.listHeaders('50/50 POSTINGS')

        if len(self.postings) == 0:
            output = 'There are no postings at the moment'

        for key in self.postings.keys():
            output += '• ' + self.postings[key]['name'] + ': ' + helper.moneyFormat(self.postings[key]['amount']) + '\n'

        return output