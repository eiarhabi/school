########################################
## CS447 Natural Language Processing  ##
##           Homework 2               ##
##       Julia Hockenmaier            ##
##       juliahmr@illnois.edu         ##
########################################
##
## Part 1:
## Evaluate the output of your bigram HMM POS tagger
##
import os.path
import sys
from operator import itemgetter
from collections import defaultdict

# A class for evaluating POS-tagged data
class Eval:
    def __init__(self, goldFile, testFile):
        self.gSens = []
        self.tSens = []
        file = open(goldFile, "r") # open the input file in read-only mode
        for line in file:
            raw = line.split()
            sentence = []
            for token in raw:
                sentence.append(token.split('_')[1])#Grab tags
            self.gSens.append(sentence) # append this list as an element to the list of sentences    
        file = open(testFile, "r") # open the input file in read-only mode
        for line in file:
            raw = line.split()
            sentence = []
            for token in raw:
                sentence.append(token.split('_')[1])
            self.tSens.append(sentence) # append this list as an element to the list of sentences
          
        self.tokenCount=0
        self.tokenError=0
        self.sentError=0
        self.sentCount=len(self.gSens)
        
        self.precision=defaultdict(lambda: defaultdict(int))
        self.recall=defaultdict(lambda: defaultdict(int))
        self.matrix=defaultdict(lambda: defaultdict(int))
        self.tags=[]
        
        for i in range(len(self.gSens)):
            badSent=False
            for j in range(len(self.gSens[i])):
                self.tokenCount+=1        
                val = self.gSens[i][j]
                guess = self.tSens[i][j]
                self.tags+=[val,guess]
                
                self.precision[guess]['count']+=1
                self.recall[val]['count']+=1
                if val!=guess:
                    self.tokenError+=1
                    badSent=True
                    self.precision[guess]['error']+=1
                    self.recall[val]['error']+=1
                self.matrix[guess][val]+=1
            if badSent:
                self.sentError+=1
        
        self.tags=list(set(self.tags))
        
                
    def getTokenAccuracy(self):
        # Return the percentage of correctly-labeled tokens
        print self.tokenError, self.tokenCount
        return 1-float(self.tokenError)/self.tokenCount
    
    def getSentenceAccuracy(self):
        return 1-float(self.sentError)/self.sentCount
    
    # Write a confusion matrix to file
    def writeConfusionMatrix(self, outFile):
        #first row list of tags
        file=open(outFile, 'w+')
        print >>file, self.tags
        for t_j in self.tags:
            row=[]
            for t_i in self.tags:
                row.append(self.matrix[t_j][t_i])
            print >>file, row

    # Return the tagger's precision on predicted tag t_i
    def getPrecision(self, tagTi):
        print self.precision[tagTi]
        return 1-self.precision[tagTi]['error']/float(self.precision[tagTi]['count'])

    # Return the tagger's recall on gold tag t_j
    def getRecall(self, tagTj):
        return 1-self.recall[tagTj]['error']/float(self.recall[tagTj]['count'])
    

if __name__ == "__main__":
    # Pass in the gold and test POS-tagged data as arguments
    if len(sys.argv) < 2:
        print "Call hw2_eval_hmm.py with two arguments: gold.txt and test.txt"
    else:
        gold = sys.argv[1]
        test = sys.argv[2]
        # You need to implement the evaluation class
        eval = Eval(gold, test)
        # Calculate accuracy (sentence and token level)
        print "Token accuracy: ", eval.getTokenAccuracy()
        print "Sentence accuracy: ", eval.getSentenceAccuracy()
        # Calculate recall and precision
        print "Recall on tag NNP: ", eval.getRecall('NNP')
        print "Precision for tag NNP: ", eval.getPrecision('NNP')
        # Write a confusion matrix
        eval.writeConfusionMatrix("conf_matrix.txt")
