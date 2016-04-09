########################################
## CS447 Natural Language Processing  ##
##           Homework 2               ##
##       Julia Hockenmaier            ##
##       juliahmr@illnois.edu         ##
########################################
##
## Part 2:
## Use pointwise mutual information to compare words in the movie corpora
##
import os.path
import sys
from operator import itemgetter
from collections import defaultdict
#----------------------------------------
#  Data input 
#----------------------------------------

import math
def log2(val):
    try:
        return math.log(val, 2)
    except:
        return float("-inf")

# Read a text file into a corpus (list of sentences (which in turn are lists of words))
# (taken from nested section of HW0)
def readFileToCorpus(f):
    """ Reads in the text file f which contains one sentence per line.
    """
    if os.path.isfile(f):
        file = open(f, "r") # open the input file in read-only mode
        i = 0 # this is just a counter to keep track of the sentence numbers
        corpus = [] # this will become a list of sentences
        print "Reading file", f, "..."
        for line in file:
            i += 1
            sentence = line.split() # split the line into a list of words
            corpus.append(sentence) # append this list as an element to the list of sentences
            #if i % 1000 == 0:
            #    sys.stderr.write("Reading sentence " + str(i) + "\n") # just a status message: str(i) turns the integer i into a string, so that we can concatenate it
        return corpus
    else:
        print "Error: corpus file ", f, " does not exist"  # We should really be throwing an exception here, but for simplicity's sake, this will suffice.
        sys.exit() # exit the script

#--------------------------------------------------------------
# PMI data structure
#--------------------------------------------------------------
class PMI:
    # Given a corpus of sentences, store observations so that PMI can be calculated efficiently
    def __init__(self, corpus):
        print "\nYour task is to add the data structures and implement the methods necessary to efficiently get the pairwise PMI of words from a corpus"
        
        counts = defaultdict(int) #f(w)
        shared = defaultdict(int) #f(c)
        cooc = defaultdict(lambda: defaultdict(int)) #f(w,c)
        
        N = 0.0
        for sen in corpus:
            sen=sorted(list(set(sen))) # Better to sort the sentence once than mess around with pair comparisons
            N+=len(sen)
            counted = defaultdict(bool)
            for i in range(len(sen)):
                shared[sen[i]]+=len(sen) 
                for j in range(i+1, len(sen)):
                    cooc[sen[i]][sen[j]]+=1
                if not counted[sen[i]]:
                    counts[sen[i]]+=1
                    counted[sen[i]]=True
                
        self.N=N
        self.counts=counts
        self.cooc=cooc
        self.shared=shared

    # Return the pointwise mutual information (based on sentence (co-)occurrence frequency) for w1 and w2
    def getPMI(self, w1, w2):
        w1, w2 = self.pair(w1, w2)
        p_wc = self.cooc[w1][w2]/self.N
        p_w = self.counts[w1]/self.N
        p_c = self.shared[w2]/self.N
        val = p_wc/(p_w*p_c)
        return log2(val)

    # Given a frequency cutoff k, return the list of observed words that appear in at least k sentences
    def getVocabulary(self, k):
        print "\nSubtask 2: return the list of words where a word is in the list iff it occurs in at least k sentences"
        vocab=[]
        for w in self.counts:
            if self.counts[w]>k:
                vocab.append(w)
        return vocab
        

    # Given a list of words, return a list of the pairs of words that have the highest PMI 
    # (without repeated pairs, and without duplicate pairs (wi, wj) and (wj, wi)).
    # Each entry in the list should be a triple (pmiValue, w1, w2), where pmiValue is the
    # PMI of the pair of words (w1, w2)
    def getPairsWithMaximumPMI(self, words, N):
        import heapq
        print "\nSubtask 3: given a list of words, find the pairs with the greatest PMI"
        pmi = []
        words = sorted(words)
        for i, w_i in enumerate(words):
            w_i = words[i]
            for j, w_j in enumerate(words[i+1:]):
                w_j=words[j+i+1]
                heapq.heappush(pmi, (self.getPMI(w_i, w_j), w_i, w_j))
                if len(pmi) > N: 
                    heapq.heappop( pmi )
        print 'Starting heap'
        top_k = heapq.nlargest(N, pmi, key=itemgetter(0))
        print top_k
        return top_k

    #-------------------------------------------
    # Provided PMI methods
    #-------------------------------------------
    # Writes the first numPairs entries in the list of wordPairs to a file, along with each pair's PMI
    def writePairsToFile(self, numPairs, wordPairs, filename): 
        file=open(filename, 'w+')
        count = 0
        for (pmiValue, wi, wj) in wordPairs:
            if count > numPairs:
                break
            count += 1
            print >>file, str(pmiValue)+" "+wi+" "+wj

    # Helper method: given two words w1 and w2, returns the pair of words in sorted order
    # That is: pair(w1, w2) == pair(w2, w1)
    def pair(self, w1, w2):
        return (min(w1, w2), max(w1, w2))

#-------------------------------------------
# The main routine
#-------------------------------------------
if __name__ == "__main__":
    corpus = readFileToCorpus('movies.txt')
    pmi = PMI(corpus)
    lv_pmi = pmi.getPMI("luke", "vader")
    print "  PMI of \"luke\" and \"vader\": ", lv_pmi
    numPairs = 100
    k = 200
    #for k in 2, 5, 10, 50, 100, 200: k=2 takes ~13 min on my low power VM 
    commonWords = pmi.getVocabulary(k)    # words must appear in least k sentences
    wordPairsWithGreatestPMI = pmi.getPairsWithMaximumPMI(commonWords, numPairs)
    pmi.writePairsToFile(numPairs, wordPairsWithGreatestPMI, "pairs_minFreq="+str(k)+".txt")
    
