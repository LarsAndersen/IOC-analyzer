#!/usr/bin/env python3


import csv
from py2neo import Graph, Path

#IOC_FOLDER="data/"
IOC_FOLDER="/devel/ioc-analyzer/iocs/"
KEYWORD_WHITELIST = []
class url():
    def __init__(self, path, url, description, report):
        self.path = path
        self.url = url
        self.description = description
        self.report = [report]
        self.keywords = []
        self.cypher = ""


    def extractKeywords(self):
        if len(self.description.split(" ")) < 10:
            self.keywords = [kw for kw in self.description.split(" ")]

    def extractReports(self):
        tmpReport = []
        for r in self.report[0].split(" "):
            tmpReport.append(r)
        self.report = tmpReport

    def whitelistKeywords(self):
        tmpKeywords = [] 
        for idx, keyword in enumerate(self.keywords):
            if keyword not in KEYWORD_WHITELIST and len(keyword) > 5:
                tmpKeywords.append(keyword)
        self.keywords = tmpKeywords

    def printRaw(self):
        print("Path: {0}\n\
                URL: {1}\n\
                Description: {2}\n\
                Report: {3}\n\
                Keywords: {4}\n\n".format(self.path, self.url, self.description, self.report, self.keywords))


    def createCypher(self):
        self.cypher = ""
        graph = Graph(auth = ('neo4j','neo4j'), host="localhost",password="neo4j")
        tx = graph.begin()
        self.cypher += "MERGE (i:Indicator {name: \"%s\", type: \"url\",  url: \"u'%s\", description: \"%s\"})\n" % (self.path.encode("utf-8", "ignore"), self.url.encode("utf-8", "ignore"), self.description.replace("\"","\\\\"))

        for key, elem in enumerate(self.report):
            self.cypher += "MERGE (rep%d:Report {name: \"%s\"})\n" % (key, elem) 
            self.cypher += "CREATE UNIQUE (i)-[:MENTIONED_IN]->(rep%d)\n" % (key)

        for key, elem in enumerate(self.keywords):
            self.cypher += "MERGE (key%d:Keyword {name: \"%s\"})\n" % (key, elem) 
            for repKey in range(0, len(self.report)):
                self.cypher += "CREATE UNIQUE (key%d)-[:MENTIONED_IN]->(rep%d)\n" % (key, repKey) 
        
        tx.append(self.cypher)
        tx.commit()

class urlIOCParser():
    def __init__(self, path, csvheader, delim=";"):
        self.path = path
        self.csvheader = csvheader
        self.delim = delim
        self.indicators = []
        

    def importIOC(self):

        with open (self.path, "r") as ioc_fh:
            reader = csv.DictReader(ioc_fh, fieldnames=self.csvheader, delimiter=self.delim)
            for line in reader:
                self.indicators.append(line)
        a = 0
        for i in self.indicators:
            a+= 1
            u = url(i['path'], i['URL'], i['description'], i['references'])
            u.extractKeywords()
            u.whitelistKeywords()
            u.createCypher()

def run():
    fieldnames = ['path', 'URL','description','references']
    parser = urlIOCParser(IOC_FOLDER + "otx-url-iocs.txt", csvheader=fieldnames, delim=";")
    parser.importIOC()
    pass




if __name__ == "__main__":
    run()
