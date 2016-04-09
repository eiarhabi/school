########################################
## CS447 Natural Language Processing  ##
##           Homework 0               ##
##       Julia Hockenmaier            ##
##       juliahmr@illnois.edu         ##
########################################
##
## Read in a text file (consisting of one sentence per line) into a data structure
##
import os.path
import sys
#----------------------------------------
#  Data input 
#----------------------------------------

# Read a text file into a corpus (list of sentences (which in turn are lists of words))
def readFileToCorpus(f):
    """ Reads in the text file f which contains one sentence per line.
    """
    if os.path.isfile(f):
        file = open(f, "r") # open the input file in read-only mode
        i = 0 # this is just a counter to keep track of the sentence numbers
        corpus = [] # this will become a list of sentences
        print "reading file ", f
        for line in file:
            i += 1
            sentence = line.split() # split the line into a list of words
            corpus.append(sentence) # append this list as an element to the list of sentences
            if i % 1000 == 0:
                sys.stderr.write("Reading sentence " + str(i) + "\n") # just a status message: str(i) turns the integer i into a string, so that we can concatenate it
        return corpus
    else:
        print "Error: corpus file ", f, " does not exist"  # We should really be throwing an exception here, but for simplicity's sake, this will suffice.
        sys.exit() # exit the script

#-------------------------------------------
# Data output
#-------------------------------------------


# Print out corpus statistics:
# - how many sentences?
# - how many word tokens?
def printStats(corpus):
    wordCount=0
    sentCount=0
    for sent in corpus:
        wordCount+=len(sent)
        sentCount+=1
    print "Word count:", wordCount
    print "Sentence count:", sentCount

def getVocab(corpus):
    words=[]
    for sent in corpus:
        for word in sent:
            if word not in words:
                words.append(word)
    words = sorted(words)
    return words

#  Print out the concordance of the word at position word_i
#  in sentence sentence, e.g: 
# 
"""
>>> printConcordance(1, ["what's", 'the', 'deal', '?'])
                                  what's    the     deal ?
>>> printConcordance(1,['watch', 'the', 'movie', 'and', '"', 'sorta', '"', 'find', 'out', '.', '.', '.'])
                                   watch    the     movie and " sorta " 
>>> printConcordance(3,['so', 'what', 'are', 'the', 'problems', 'with', 'the', 'movie', '?'])
                             so what are    the     problems with the movie ?     
"""
def printConcordance(sentence, word_i):
    """ print out the five words preceding word,
        the word at position i and the folllowing five words."""
    if word_i < len(sentence):
        start = max(word_i-5, 0)
        end = min(word_i+6, len(sentence))
        left = ' '.join(sentence[start:word_i])
        right = ' '.join(sentence[word_i+1:end])
        print left.rjust(40), sentence[word_i].center(10), right.ljust(30)



#--------------------------------------------------------------
# Corpus analysis (tokens as class)
#--------------------------------------------------------------

# We use the class Token to point to individual tokens (words) in the corpus.
class Token:
    def __init__(self, s, w): # we need to initialize each instance of Token:
        self.sentence = s # sentence is the index of the sentence (in the corpus)
        self.word = w # word is the index of the word (in the sentence)

#--------------------------------------------------------------
# Corpus analysis (tokens as tuple (i, j))
#--------------------------------------------------------------

#
# Create an index that maps each word to all its positions in the corpus
# (tokens are encoded as a tuple)
#
def createCorpusIndex_TupleVersion(corpus):
    from collections import defaultdict
    tupleIndex=defaultdict(list)

    for i in range(len(corpus)):
        for j in range(len(corpus[i])):
            tupleIndex[corpus[i][j]].append((i,j))
    return tupleIndex
        
def printWordFrequencies_TupleVersion(index, vocab):
    sortTuples = sorted(index.items(), key=lambda x: len(x[1]), reverse=True)
    sortWords = [(x[0], len(x[1])) for x in sortTuples]
    print sortWords

def printCorpusConcordance_TupleVersion(word, corpus, index):
    for token in index[word]:
        printConcordance(corpus[token[0]], token[1])

def createCorpusIndex_ClassVersion(corpus):
    from collections import defaultdict
    tupleIndex=defaultdict(list)

    for i in range(len(corpus)):
        for j in range(len(corpus[i])):
            tupleIndex[corpus[i][j]].append(Token(i,j))
    return tupleIndex

def printWordFrequencies_ClassVersion(index, vocab):
    sortTokens = sorted(index.items(), key=lambda x: len(x[1]), reverse=True)
    sortWords = [(x[0], len(x[1])) for x in sortTokens]
    print sortWords

def printCorpusConcordance_ClassVersion(word, corpus, index):
    for token in index[word]:
        printConcordance(corpus[token.sentence], token.word)

#-------------------------------------------
# The main routine
#-------------------------------------------
if __name__ == "__main__":
    movieCorpus = readFileToCorpus('movies.txt')
    printStats(movieCorpus)
    movieVocab = getVocab(movieCorpus)
    movieIndexTuples = createCorpusIndex_TupleVersion(movieCorpus)
    printWordFrequencies_TupleVersion(movieIndexTuples, movieVocab)
    printCorpusConcordance_TupleVersion("the", movieCorpus, movieIndexTuples)
    movieIndexClass = createCorpusIndex_ClassVersion(movieCorpus)
    printWordFrequencies_ClassVersion(movieIndexClass, movieVocab)
    printCorpusConcordance_ClassVersion("the", movieCorpus, movieIndexClass)
