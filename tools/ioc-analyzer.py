#!/usr/bin/env

from py2neo import Graph
import csv

KEYWORD_WHITELIST = []
MAX_DESCRIPTION_KEYWORD_LENGTH = 10
PATH = "data/"

class IndicatorError(Exception):
    def __init__(self, message):
        self.message = message
        print(self.message)

class IndicatorBase:
    def __init__(self, value, description, reference, type):
        self.type = type
        self.description = description
        self.reference = reference
        self.value = value

    def returnAttributes(self):
        return self.__dict__

    def commitCypher(self, obj):
        graph = Graph(auth = ('neo4j','neo4j'), host="localhost",password="neo4j")
        tx = graph.begin()
        self.cypher = ""
        if isinstance(obj, Url):
            pass
        elif isinstance(obj, IP):
            pass
        elif isinstance(obj, Hash):
            pass
        elif isinstance(obj, Domain):
            pass
        else:
            raise IndicatorError("Indicator type is not supported.")

        attributes = obj.__dict__

        attributes['reference'] = self.extractReference()
        keywords = self.extractKeywords()
        keywords = self.whitelistKeywords() 
        self.cypher += "MERGE (i:Indicator {value: \"%s\", type: \"%s\",  description: \"%s\"})\n" % (self.value, self.type,self.description)

        for key, elem in enumerate(self.reference):
            self.cypher += "MERGE (rep%d:Report {name: \"%s\"})\n" % (key, elem)
            self.cypher += "CREATE UNIQUE (i)-[:MENTIONED_IN]->(rep%d)\n" % (key)

        for key, elem in enumerate(self.keywords):
            self.cypher += "MERGE (key%d:Keyword {name: \"%s\"})\n" % (key, elem)
            for repKey in range(0, len(self.reference)):
                self.cypher += "CREATE UNIQUE (key%d)-[:MENTIONED_IN]->(rep%d)\n" % (key, repKey)
        tx.append(self.cypher)
        tx.commit()

    def extractKeywords(self):
        if len(self.description.split(" ")) < MAX_DESCRIPTION_KEYWORD_LENGTH:
            self.keywords = [kw for kw in self.description.split(" ")]

    def extractReference(self):
        tmpReference= []
        try:
            for r in self.reference.split(" "):
                tmpReference.append(r)
        except IndexError:
            tmpReference = self.reference
        return tmpReference 

    def whitelistKeywords(self):
        #TODO: This can probably be improved 
        tmpKeywords = []
        for idx, keyword in enumerate(self.keywords):
            if keyword not in KEYWORD_WHITELIST and len(keyword) > 5:
                tmpKeywords.append(keyword)
        self.keywords = tmpKeywords

    def loadIOC(self, path, url="", domain="", hash="", ip=""):
        indicatorList = []
        if url:
            with open(path + url, "r") as url_fh:
                reader = csv.DictReader(url_fh, fieldnames=["value", "description","reference"], delimiter=";")
                for line in reader:
                    indicatorList.append(line)
            for i in indicatorList:
                u = Url(i['value'], i['description'], i['reference'])
                u.add()

class Url(IndicatorBase):
    def __init__(self, value, description, reference):
        super(Url, self).__init__(value, description, reference, type="url")

    def print(self):
        print(self.returnAttributes())
        self.commitCypher(self)

    def enrich(self):
        pass

    def add(self):
        self.commitCypher(self)


class IP(IndicatorBase):
    def __init__(self, value, description, reference):
        super(Url, self).__init__(value, description, reference, type="IP")

    def print(self):
        print(self.returnAttributes())

class Hash(IndicatorBase):
    def __init__(self, value, description, reference):
        super(Url, self).__init__(value, description, reference, type="hash")

    def print(self):
        print(self.returnAttributes())
        self.commitCypher("test", self)

class Domain(IndicatorBase):
    def __init__(self, value, description, reference):
        super(Url, self).__init__(value, description, reference, type="domain")

    def print(self):
        print(self.returnAttributes())
        self.commitCypher("test", self)

def loadIOC(path, url="", domain="", hash="", ip=""):
    """ Helper function for loading IOCs """
    indicatorList = []
    if url:
        with open(path + url, "r") as url_fh:
            reader = csv.DictReader(url_fh, fieldnames=["value", "description","reference"], delimiter=";")
            for line in reader:
                indicatorList.append(line)
        for i in indicatorList:
            u = Url(i['value'], i['description'], i['reference'])
            u.add()
if __name__ == "__main__":
    loadIOC(PATH, url="url.csv")
