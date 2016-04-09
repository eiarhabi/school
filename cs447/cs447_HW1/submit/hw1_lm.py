########################################
## CS447 Natural Language Processing  ##
##           Homework 1               ##
##       Julia Hockenmaier            ##
##       juliahmr@illnois.edu         ##
########################################
##
## Part 1:
## Develop a smoothed n-gram language model and evaluate it on a corpus
##
import os.path
import sys
import random
import math
from operator import itemgetter
from collections import defaultdict
#----------------------------------------
#  Data input 
#----------------------------------------

# Read a text file into a corpus (list of sentences (which in turn are lists of words))
# (taken from nested section of HW0)
def readFileToCorpus(f):
    """ Reads in the text file f which contains one sentence per line.
    """
    if os.path.isfile(f):
        file = open(f, "r") # open the input file in read-only mode
        i = 0 # this is just a counter to keep track of the sentence numbers
        corpus = [] # this will become a list of sentences
        print "Reading file ", f
        for line in file:
            i += 1
            sentence = line.split() # split the line into a list of words
            #append this lis as an element to the list of sentences
	    corpus.append(sentence)
            if i % 1000 == 0:
		#print a status message: str(i) turns int i into a string
		#so we can concatenate it
                sys.stderr.write("Reading sentence " + str(i) + "\n")
	    #endif
	#endfor
        return corpus
    else:
	#ideally we would throw an exception here, but this will suffice
        print "Error: corpus file ", f, " does not exist"
        sys.exit() # exit the script
    #endif
#enddef


# Preprocess the corpus to help avoid sess the corpus to help avoid sparsity
def preprocess(corpus):
    #find all the rare words
    freqDict = defaultdict(int)
    for sen in corpus:
        for word in sen:
            freqDict[word] += 1

    #replace rare words with unk
    for sen in corpus:
        for i in range(0, len(sen)):
            word = sen[i]
            if freqDict[word] < 2:
                sen[i] = UNK

    #bookend the sentences with start and end tokens
    for sen in corpus:
        sen.insert(0, start)
        sen.append(end)

    return corpus

def preprocessTest(vocab, corpus):
    #replace test words that were unseen in the training with unk
    for sen in corpus:
        for i in range(0, len(sen)):
            word = sen[i]
            if word not in vocab:
                sen[i] = UNK

    
    #bookend the sentences with start and end tokens
    for sen in corpus:
        sen.insert(0, start)
        sen.append(end)

    return corpus

# Constants 
UNK = "UNK"     # Unknown word token
start = "<s>"   # Start-of-sentence token
end = "</s>"    # End-of-sentence-token


#--------------------------------------------------------------
# Language models and data structures
#--------------------------------------------------------------

# Parent class for the three language models you need to implement
class LanguageModel:
    # Initialize and train the model (ie, estimate the model's underlying probability
    # distribution from the training corpus)
    def __init__(self, corpus):
        print """Your task is to implement three kinds of n-gram language models:
      a) an (unsmoothed) unigram model (UnigramModel)
      b) a unigram model smoothed using Laplace smoothing (SmoothedUnigramModel)
      c) an unsmoothed bigram model (BigramModel)
      d) a bigram model smoothed using absolute discounting (SmoothedBigramModel)
      """

    # Generate a sentence by drawing words according to the 
    # model's probability distribution
    # Note: think about how to set the length of the sentence 
    #in a principled way
    def generateSentence(self):
        sent=[]
        word = start
        while word != end:
            sent.append(word)
            word=self.dist.draw()
        sent.append(end)
        return sent


    # Given a sentence (sen), return the probability of 
    # that sentence under the model
    def getSentenceProbability(self, sen):
        prob=1.0
        for word in sen[1:]:
            prob*=self.dist.prob(word)
        return prob

    # Given a corpus, calculate and return its perplexity 
    #(normalized inverse log probability)
    def getCorpusPerplexity(self, corpus):
        words = [word for sen in corpus for word in sen[1:]]
        log_sum = 0.0
        for word in words:
            P=self.dist.prob(word)
            if P!= 0:
                log_sum += math.log(self.dist.prob(word))
        return math.exp(log_sum/-len(words))

    # Given a file (filename) and the number of sentences, generate a list
    # of sentences and write each to file along with its model probability.
    # Note: you shouldn't need to change this method
    def generateSentencesToFile(self, numberOfSentences, filename):
        file=open(filename, 'w+')
        for i in range(0,numberOfSentences):
            sen = self.generateSentence()
            prob = self.getSentenceProbability(sen)
            print >>file, prob, " ", sen

# Unigram language model
class UnigramModel(LanguageModel):
    def __init__(self, corpus):
        self.dist = UnigramDist(corpus)

#Smoothed unigram language model (use laplace for smoothing)
class SmoothedUnigramModel(LanguageModel):
    def __init__(self, corpus):
        self.dist = SmoothUnigramDist(corpus)

# Unsmoothed bigram language model
class BigramModel(LanguageModel):
    def __init__(self, corpus):
        self.dist = BigramDist(corpus)

    def generateSentence(self):
        sent=[start]
        word = self.dist.draw(start)
        while word != end:
            sent.append(word)
            word=self.dist.draw(word)
        sent.append(end)
        return sent

    # Given a sentence (sen), return the probability of 
    # that sentence under the model
    def getSentenceProbability(self, sen):
        prior=start
        prob=1.0
        for word in sen[1:]:
            prob*=self.dist.prob(word, prior)
            prior=word
        return prob

    # Given a corpus, calculate and return its perplexity 
    #(normalized inverse log probability)
    def getCorpusPerplexity(self, corpus):
        prior=start
        words = (word for sen in corpus for word in sen)
        next(words)
        word_len=0
        log_sum = 0.0
        for word in words:
            try:
                log_sum += math.log(self.dist.prob(word, prior))
                word_len+=1
            except:
                pass#Underflow on <s> </s>
                # print word, prior, word_len
            prior=word
        return math.exp(log_sum/-word_len)

# Smoothed bigram language model (use absolute discounting for smoothing)
class SmoothedBigramModel(LanguageModel):
    def __init__(self, corpus):
        self.dist = SmoothBigramDist(corpus)

    def generateSentence(self):
        sent=[start]
        word = self.dist.draw(start)
        while word != end:
            sent.append(word)
            word=self.dist.draw(word)
        sent.append(end)
        return sent

    # Given a sentence (sen), return the probability of 
    # that sentence under the model
    def getSentenceProbability(self, sen):
        prior=start
        prob=0.
        for word in sen[1:]:
            prob+=math.log(self.dist.prob(word, prior))
            #print 'DIST'
            #prob*=self.dist.prob(word, prior)
            #print math.log(self.dist.prob(word, prior)), word, prior
            prior=word
            
        return math.exp(prob)
        #return prob

    # Given a corpus, calculate and return its perplexity 
    #(normalized inverse log probability)
    def getCorpusPerplexity(self, corpus):
        prior=start
        words = (word for sen in corpus for word in sen)
        next(words)
        word_len=0
        log_sum = 0.0
        for word in words:
            word_len+=1
            try:
                log_sum += math.log(self.dist.prob(word, prior))
                
            except:
                #pass#Underflow on <s> </s>
                print word, prior, word_len
            prior=word
            if word_len%100000==0:
                print word_len
        return math.exp(log_sum/-word_len)


# Sample class for a unsmoothed unigram probability distribution
# Note: 
#       Feel free to use/re-use/modify this class as necessary for your 
#       own code (e.g. converting to log probabilities after training). 
#       This class is intended to help you get started
#       with your implementation of the language models above.
class UnigramDist:
    def __init__(self, corpus):
        self.counts = defaultdict(float)
        self.total = 0.0
        self.train(corpus)

    # Add observed counts from corpus to the distribution
    def train(self, corpus):
        for sen in corpus:
            for word in sen:
                self.counts[word] += 1.0
                self.total += 1.0
        self.total -= self.counts[start]
        self.counts.pop(start)

    # Returns the probability of word in the distribution
    def prob(self, word):
        return self.counts[word]/self.total

    # Generate a single random word according to the distribution
    def draw(self):
        rand = random.random()
        for word in self.counts.keys():
            rand -= self.prob(word)
            if rand <= 0.0:
                return word

class SmoothUnigramDist:
    def __init__(self, corpus):
        self.counts = defaultdict(float)
        self.total = 0.0
        self.train(corpus)

    # Add observed counts from corpus to the distribution
    def train(self, corpus):
        for sen in corpus:
            for word in sen:
                self.counts[word] += 1.0
                self.total += 1.0
        self.total -= self.counts[start]
        self.counts.pop(start)
        self.S = S = len(self.counts.keys())


    # Returns the probability of word in the distribution
    def prob(self, word):
        return (self.counts[word]+1.)/(self.total+self.S)

    # Generate a single random word according to the distribution
    def draw(self):
        rand = random.random()
        for word in self.counts.keys():
            rand -= self.prob(word)
            if rand <= 0.0:
                return word

class BigramDist:
    def __init__(self, corpus):
        self.priors = defaultdict(lambda : defaultdict(float))
        self.total = defaultdict(float)
        self.train(corpus)

    # Add observed counts from corpus to the distribution
    def train(self, corpus):
        for sen in corpus:
            for i in range(len(sen)-1):
                j=i+1
                self.priors[sen[i]][sen[j]]+=1
                self.total[sen[i]]+=1

    # Returns the probability of word in the distribution
    def prob(self, word, prior):
        return self.priors[prior][word]/self.total[prior]

    # Generate a single random word according to the distribution
    def draw(self, prior):
        rand = random.random()
        for word in self.priors[prior].keys():
            rand -= self.prob(word, prior)
            if rand <= 0.0:
                return word

class SmoothBigramDist:
    def __init__(self, corpus):
        self.priors = defaultdict(lambda : defaultdict(float))
        self.total = defaultdict(float)
        self.train(corpus)
        self.smooth_unigram = SmoothUnigramDist(corpus)


    # Add observed counts from corpus to the distribution
    def train(self, corpus):
        for sen in corpus:
            for i in range(len(sen)-1):
                j=i+1
                self.priors[sen[i]][sen[j]]+=1
                self.total[sen[i]]+=1
        n_1=0.0
        n_2=0.0
        for prior in self.priors.keys():
            for c in self.priors[prior].values():
                if c==1:
                    n_1+=1
                elif c==2:
                    n_2+=1
        self.discount = n_1/(n_1+2*n_2)

    # Returns the probability of word in the distribution
    def prob(self, word, prior):
        if prior==end:
            prior=start
        try:
            s_1 = max(self.priors[prior][word]-self.discount, 0)/self.total[prior]
        except:
            print 'error s_1'
            s_1 = 0
        try:
            s_2 = self.discount*len(self.priors[prior].keys())*self.smooth_unigram.prob(word)/self.total[prior]
        except: 
            print 'error', prior
            #s_2 = self.discount*len(self.priors[prior].keys())*self.smooth_unigram.prob(word)/self.total[start]
            s_2 = 0
       # print s_2

        if (s_1+s_2)==0:
            print 'Underflow', word, prior
            print s_1, s_2, self.total[prior]
            return 1.
        else:
            return s_1+s_2

        

    # Generate a single random word according to the distribution
    def draw(self, prior):
        rand = random.random()
        for word in self.priors[prior].keys():
            rand -= self.prob(word, prior)
            if rand <= 0.0:
                return word
        return end
        
#-------------------------------------------
# The main routine
#-------------------------------------------
if __name__ == "__main__":
    #read your corpora
    trainCorpus = readFileToCorpus('train.txt')
    trainCorpus = preprocess(trainCorpus)
    posTestCorpus = readFileToCorpus('pos_test.txt')
    negTestCorpus = readFileToCorpus('neg_test.txt')
    vocab = set()
    print """Task 0: create a vocabulary 
(collection of word types) for the train corpus"""
    posTestCorpus = preprocessTest(vocab, posTestCorpus)
    negTestCorpus = preprocessTest(vocab, negTestCorpus)
    unigram = UnigramModel(trainCorpus)
    smooth_unigram = SmoothedUnigramModel(trainCorpus)
    bigram = BigramModel(trainCorpus)
    smooth_bigram = SmoothedBigramModel(trainCorpus)

    '''
    # Run sample unigram dist code
    unigramDist = UnigramDist(trainCorpus)
    print "Sample UnigramDist output:"
    print "Probability of \"vader\": ", unigramDist.prob("vader")
    print "Probability of \""+UNK+"\": ", unigramDist.prob(UNK)
    print "\"Random\" draw: ", unigramDist.draw()
    # Sample test run for unigram model
    print 'UNIGRAM'
    unigram = UnigramModel(trainCorpus)
    # Task 1   (*** remember to generate 20 sentences for final output ***)
    unigram.generateSentencesToFile(20, "unigram_output.txt")
    print 'Perp', unigram.getCorpusPerplexity(trainCorpus)

    print 'SMOOTH UNIGRAM'
    smoothUnigram = SmoothedUnigramModel(trainCorpus)
    smoothUnigram.generateSentencesToFile(20, "smooth_unigram_output.txt")
    print 'Perp', smoothUnigram.getCorpusPerplexity(trainCorpus)
    '''
    print 'BIGRAM'
    bigram = BigramModel(trainCorpus)
    bigram.generateSentencesToFile(20, "bigram_output.txt")
    #print 'Perp', bigram.getCorpusPerplexity(trainCorpus)
    '''
    print 'SMOOTH BIGRAM'
    smooth_bigram = SmoothedBigramModel(trainCorpus)
    smooth_bigram.generateSentencesToFile(20, "smooth_bigram_output.txt")
    print smooth_bigram.getCorpusPerplexity(trainCorpus)
    
    '''
    # Task 2
    posTestCorpus = readFileToCorpus('pos_test.txt')
    negTestCorpus = readFileToCorpus('neg_test.txt')
    trainPerp = bigram.getCorpusPerplexity(trainCorpus)
    posPerp = bigram.getCorpusPerplexity(posTestCorpus)
    negPerp = bigram.getCorpusPerplexity(negTestCorpus)   
    print "Perplexity of positive training corpus:    "+ str(trainPerp) 
    print "Perplexity of positive review test corpus: "+ str(posPerp)
    print "Perplexity of negative review test corpus: "+ str(negPerp)
