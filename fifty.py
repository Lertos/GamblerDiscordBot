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
        if userId in self.postings.keys():
            return True
        return False


    #Returns a bool whether or not the given name has a posting or not
    def doesNameExistInPosting(self, name):
        for key in self.postings.keys():
            if self.postings[key]['name'].lower() == name.lower():
                return True
        return False


    #Create posting with the given amount
    def createPosting(self, userId, name, amount):
        if userId in self.postings.keys():
            return False
        
        self.postings[userId] = {}

        self.postings[userId]['name'] = name
        self.postings[userId]['amount'] = amount

        self.savePostings()

        return True


    #Returns a string with all the postings
    def displayPostings(self):
        output = '===== 50/50 POSTINGS =====\n'

        if len(self.postings) == 0:
            output = 'There are no postings at the moment'

        for key in self.postings.keys():
            output += '• ' + self.postings[key]['name'] + ': ' + helper.moneyFormat(self.postings[key]['amount']) + '\n'

        return output