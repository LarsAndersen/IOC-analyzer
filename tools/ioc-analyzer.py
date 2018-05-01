#!/usr/bin/env

#from py2neo import Graph
import csv

KEYWORD_WHITELIST = []
MAX_DESCRIPTION_KEYWORD_LENGTH = 10
PATH = "data/"

class IndicatorError(Exception):
    def __init__(self, message):
        self.message = message
        print(self.message)

class IndicatorBase:
    def __init__(self, attributes, type):
        self.type = type
        self.description = attributes['description']
        self.reference = attributes['reference']
        self.value = attributes['value']
        self.extraAttributes = attributes

        del self.extraAttributes['description']
        del self.extraAttributes['reference']
        del self.extraAttributes['value']

    def processAttributes(self):
        if isinstance(self, Url):
            pass
        elif isinstance(self, IP):
            pass
        elif isinstance(self, Hash):
            pass
        elif isinstance(self, Domain):
            pass
        else:
            raise IndicatorError("Indicator type is not supported.")

        self.extractReference()
        self.extractKeywords()
        self.whitelistKeywords()


    def extractMetadata(self):
        # Author
        # Year
        # targetCountry
        pass



    def writeExtraAttributes(self):
        extra = ""
        for attribute in self.extraAttributes:
            extra += ", %s: \"%s\"" % (attribute, self.extraAttributes[attribute])
        return extra

    def buildCypher(self):
        self.cypher = ""
        self.cypher += "MERGE (i:Indicator {value: \"%s\", type: \"%s\",  description: \"%s\" %s})\n" \
                            % (self.value, self.type,self.description, self.writeExtraAttributes())

        for key, elem in enumerate(self.reference):
            self.cypher += "MERGE (rep%d:Report {name: \"%s\"})\n" % (key, elem)
            self.cypher += "CREATE UNIQUE (i)-[:MENTIONED_IN]->(rep%d)\n" % (key)

        for key, elem in enumerate(self.keywords):
            self.cypher += "MERGE (key%d:Keyword {name: \"%s\"})\n" % (key, elem)
            for repKey in range(0, len(self.reference)):
                self.cypher += "CREATE UNIQUE (key%d)-[:MENTIONED_IN]->(rep%d)\n" % (key, repKey)

    def commitCypher(self):
        graph = Graph(auth = ('neo4j','neo4j'), host="localhost",password="neo4j")
        tx = graph.begin()
        tx.append(self.cypher)
        tx.commit()
        pass
    def extractKeywords(self):
        if len(self.description.split(" ")) < MAX_DESCRIPTION_KEYWORD_LENGTH:
            self.keywords = [kw for kw in self.description.split(" ")]


    def extractReference(self):
        tmpReference= []
        try:
            for r in self.reference.split(" "):
                tmpReference.append(r)
        except IndexError:
            pass
        self.reference = tmpReference

    def whitelistKeywords(self):
        #TODO: This can probably be improved
        tmpKeywords = []
        try:
            for idx, keyword in enumerate(self.keywords):
                if keyword not in KEYWORD_WHITELIST and len(keyword) > 5:
                    tmpKeywords.append(keyword)
        except TypeError:
            pass
        self.keywords = tmpKeywords

    def loadIOC(self, path, url="", domain="", hash="", ip=""):
        pass

class Url(IndicatorBase):
    def __init__(self, attributes):
        super(Url, self).__init__(attributes, type="url")

    def printSelf(self):
        print(self.returnAttributes())
        self.commitCypher(self)

    def enrich(self):
        #IDEA Extract parameters
        #IDEA special character count

        pass

class IP(IndicatorBase):
    def __init__(self, value, description, reference):
        super(Url, self).__init__(value, description, reference, type="IP")

    def printSelf(self):
        print(self.returnAttributes())

    def enrich(self):
        #IDEA whois
        #IDEA geo
        #IDEA ASN
        pass


class Hash(IndicatorBase):
    def __init__(self, value, description, reference):
        super(Url, self).__init__(value, description, reference, type="hash")

    def printSelf(self):
        print(self.returnAttributes())
        self.commitCypher("test", self)

class Domain(IndicatorBase):
    def __init__(self, value, description, reference):
        super(Url, self).__init__(value, description, reference, type="domain")

    def printSelf(self):
        print(self.returnAttributes())
        self.commitCypher()

def loadIOC(path, url="", domain="", hash="", ip=""):
    """ Helper function for loading IOCs """
    indicatorList = []
    if url:
        with open(path + url, "r") as url_fh:
            reader = csv.DictReader(url_fh, fieldnames=["value", "url", "description","reference"], delimiter=";")
            for line in reader:
                indicatorList.append(line)
        for i in indicatorList:
            u = Url(i)
            u.processAttributes()
            u.buildCypher()
            u.commitCypher()
if __name__ == "__main__":
    loadIOC(PATH, url="url.csv")
