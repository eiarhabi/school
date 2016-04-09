import sys, os, math, codecs
from collections import defaultdict
from operator import itemgetter

#log base 2
def log(prob):
    if prob>0:
        return math.log(prob, 2)
    return 0#float('-inf')

# An unsmoothed unigram probability distribution (edit as needed)
class Dist:
    def __init__(self):
        self.counts = {}
        self.total = 0.0

    # Add an observed count to the distribution
    def addCount(self, outcome, count):
        if outcome not in self.counts:
            self.counts[outcome] = 0.0
        self.counts[outcome] += count
        self.total += count

    # Returns the set of observed words (including UNK if applicable)
    def getVocabulary(self):
        return self.counts.keys()

    # Returns the log of the probability of outcome in the distribution
    def logprob(self, outcome):
        num = self.counts[outcome]
        if num > 0:
            return log(self.counts[outcome]/self.total)
        return float('-inf')

    # Returns the log of the probability of outcome in the distribution
    def prob(self, outcome):
        num = self.counts[outcome]
        if num > 0:
            return num/self.total
        return 0.0

# An unsmoothed conditional probability distribution (edit as needed)
class ConditionalDist:
    def __init__(self):
        self.dists = {}

    # Adds an observed event outcome|cond to the distribution
    def addCount(self, cond, outcome, count):
        if cond not in self.dists:
            self.dists[cond] = Dist()
        self.dists[cond].addCount(outcome, count)
        
    # Returns the log of the probability of a outcome|cond event according to this distribution
    def logprob(self, cond, outcome):
        if cond not in self.dists:
            return float('-inf')
        return self.dists[cond].logprob(outcome)
        
    # Returns the probability of a outcome|cond event according to this distribution
    def prob(self, cond, outcome):
        if cond not in self.dists:
            return 0.0
        return self.dists[cond].prob(outcome)

# Constant for NULL word at position zero in target sentence
NULL = "NULL"

# Constant for delimiter in alignment output
DELIMITER = "================================"

# Your task is to finish implementing IBM Model 1 in this class
class IBMModel1:    
    def __init__(self, trainingCorpusFile):
        # Initialize data structures for storing training data
        self.fCorpus = []                   # fCorpus is a list of source (e.g. Spanish) sentences

        self.tCorpus = []                   # tCorpus is a list of target (e.g. English) sentences 
                                            # (tCorpus[i] is the translation of fCorpus[i])
        self.trans = {}                     # trans[e_x][f_y] is initialized with a count of how often target word e_x and source word f_y appear together.
        self.tLenProb = defaultdict(lambda: defaultdict(float))
        self.wTranProb = defaultdict(lambda: defaultdict(float))
        self.counts = defaultdict(lambda: defaultdict(float))

        # Read the corpus
        self.initialize(trainingCorpusFile);
        # Initialize any additional data structures here (e.g. for probability model)

    # Reads a corpus of parallel sentences from a text file (you shouldn't need to modify this method)
    def initialize(self, fileName):
        file = codecs.open(fileName, "r", "utf-8")
        i = 0
        j = 0;
        tTokenized = ();
        fTokenized = ();
        for s in file:
            if i == 0:      
                tTokenized = s.split()
                # Add null word in position zero
                tTokenized.insert(0, NULL)
                self.tCorpus.append(tTokenized)
            elif i == 1:           
                fTokenized = s.split()
                self.fCorpus.append(fTokenized)
                for tw in tTokenized:
                    if tw not in self.trans:
                        self.trans[tw] = {};
                    for fw in fTokenized:
                        if fw not in self.trans[tw]:
                             self.trans[tw][fw] = 1
                        else:
                            self.trans[tw][fw] = self.trans[tw][fw] +1
            else:
                i = -1
                j += 1
            i +=1
            if j%1000==0:
                print j
        file.close()
        return
    
    # Uses the EM algorithm to learn the model's parameters
    # Feel free to use fewer iterations during development; each round of EM may take a little while
    # convergenceEpsilon is the parameter for log-likelihood-based convergence (for 2 points extra credit; see the handout)
    def trainUsingEM(self, numIterations=20, convergenceEpsilon=0.1, useConvergenceEpsilon=False):
        ###
        # Part 1: Train the model using the EM algorithm
        #
        # <you need to finish implementing this method's sub-methods>
        #
        ###

        # Compute translation length probabilities q(m|n)
        self.computeTranslationLengthProbabilities()         # <you need to implement computeTranslationlengthProbabilities()>
        # Set initial values for the translation probabilities p(f_y|e_x)
        self.initializeWordTranslationProbabilities()        # <you need to implement initializeTranslationProbabilities()>

        # By default, run for numIterations; for the extra credit (see section 1.4.4 of handout), change the body of this method to 
        # use the convergenceEpsilon criteria for convergence when useConvergenceEpsilon is True
        if useConvergenceEpsilon:
            L0 = 1.0
            for i in range(numIterations):
                print 'iteration:', i
                # Run E-step: calculate expected counts using current set of parameters
                self.computeExpectedCounts()                     # <you need to implement computeExpectedCounts()>
                # Run M-step: use the expected counts to re-estimate the parameters
                self.updateTranslationProbabilities()            # <you need to implement updateTranslationProbabilities()>
                sum_ = 0.0
                for s in range(len(self.tCorpus)):
                    n = len(self.fCorpus[s])
                    m = len(self.tCorpus[s])
                    sum_+=log(self.getTranslationLengthProbability(n,m))-m*log(n+1)# Not necessary since same for all
                    reverse = defaultdict(lambda: defaultdict(float))
                    for e_x in self.tCorpus[s]:
                        for f_y in self.fCorpus[s]:
                            reverse[f_y][e_x] = self.wTranProb[e_x][f_y]
                    for f_y in reverse:
                        inner = 0.0
                        for e_i in reverse:
                            inner+=reverse[f_y][e_i]
                        #print inner
                        sum_+=log(inner)
                L = 1.*sum_/len(self.tCorpus)
                
                if L0-L<convergenceEpsilon:
                    print 'stopping...L:', L0-L
                    break
                else:
                    print 'Improvement:', L0-L
                    L0=L
        else:
            for i in range(numIterations):
                print 'iteration:', i
                # Run E-step: calculate expected counts using current set of parameters
                self.computeExpectedCounts()                     # <you need to implement computeExpectedCounts()>
                # Run M-step: use the expected counts to re-estimate the parameters
                self.updateTranslationProbabilities()            # <you need to implement updateTranslationProbabilities()>
    
    # Compute translation length probabilities q(m|n), where m is the length of a non-English (source) sentence and n is the length of an English (target) sentence
    def computeTranslationLengthProbabilities(self):
        
        for idx, e in enumerate(self.tCorpus):
            self.tLenProb[len(e)][len(self.fCorpus[idx])]+=1
            
        for n in self.tLenProb:
            total = float(sum(self.tLenProb[n].values()))
            for m in self.tLenProb[n]:
                self.tLenProb[n][m] /= total
        #print 'Dictionary of n lengths and frequentist probability of m lengths', self.tLenProb

    # Set initial values for the translation probabilities p(f_y|e_x)
    def initializeWordTranslationProbabilities(self):
        for e_x in self.trans:
            total = float(sum(self.trans[e_x].values()))
            for f_y in self.trans[e_x]:
                self.wTranProb[e_x][f_y] = self.trans[e_x][f_y]/total
                

    # Run E-step: calculate expected counts using current set of parameters
    # THANKS! https://piazza.com/class/idiy67yf3qu74?cid=336
    def computeExpectedCounts(self):
        senCounts = []
        for s, e in enumerate(self.tCorpus):
            senCounts.append(defaultdict(lambda: defaultdict(int)))
            denom = 0.
            for f_j in self.fCorpus[s]:
                for e_i in e:
                    denom+=self.getWordTranslationProbability(f_j, e_i)
                for e_i in e:
                    numer = self.getWordTranslationProbability(f_j, e_i)
                    senCounts[s][e_i][f_j]=numer/denom
                    
        for s in range(len(senCounts)):
            for e_i in senCounts[s]:
                for f_y in senCounts[s][e_i]:
                    self.counts[e_i][f_y]+=senCounts[s][e_i][f_y]
      

    # Run M-step: use the expected counts to re-estimate the parameters
    def updateTranslationProbabilities(self):
        for e_x in self.counts:
            Z = 0.0
            for f_y in self.counts[e_x]:
                Z+=self.counts[e_x][f_y]
            for f_y in self.counts[e_x]:
                self.wTranProb[e_x][f_y]= self.counts[e_x][f_y]/Z
                

    # Returns the best alignment between nonEnglishSen and englishSen, according to your model
    def align(self, nonEnglishSen, englishSen):
        ###
        # Part 2: Find and return the best alignment
        #
        # <you need to finish implementing this method>
        #        
        ###
    
        # Double-check that englishSen has a null word in position zero, and add it if not
        if englishSen[0] != NULL:
            englishSen.insert(0, NULL)
        
        alignment = []
        for j, f_j in enumerate(nonEnglishSen):
            max_, midx = 0, -1
            for i, e_i in enumerate(englishSen):
                if self.wTranProb[e_i][f_j]>max_:
                    max_=self.wTranProb[e_i][f_j]
                    midx=i
            alignment.append(midx)
                    
        
        return alignment   # Your code above should return the correct alignment instead

    # Return q(m|n), where m is the length of a non-English (source) sentence and n is the length of an English (target) sentence
    # (Can either return log probability or regular probability)
    def getTranslationLengthProbability(self, n, m):
        #return log(self.tLenProb[n][m])
        return self.tLenProb[n][m]

    # Return p(f_y | e_x), the probability that English word e_x generates non-English word f_y
    # (Can either return log probability or regular probability)
    def getWordTranslationProbability(self, f_y, e_x):
        #return log(self.wTranProb[e_x][f_y])
        return self.wTranProb[e_x][f_y]     

    # Utility method to calculate and write alignments to file
    def generateAndSaveAlignments(self, outFile):
        file = codecs.open(outFile, "w", "utf-8")
        for s in range(0, len(self.fCorpus)):
            fSen = self.fCorpus[s]
            tSen = self.tCorpus[s]
            #print "Aligning sentence "+str(s+1)+" out of "+str(len(self.fCorpus))
            file.write(" ".join(tSen)+"\n")
            file.write(" ".join(fSen)+"\n")
            file.write(" ".join(str(x) for x in self.align(fSen, tSen))+"\n")
            file.write(DELIMITER+"\n")
        file.close()
        print "Alignments written to "+outFile
    
if __name__ == "__main__":
    # Initialize model
    model = IBMModel1('eng-spa_small.txt')
    # Train model
    model.trainUsingEM(20, True); # may want to use fewer than 10 iterations during dev
    # Use model to generate alignments
    print "Calculating and saving alignments"
    outFile = "eng-spa_small.aligned.txt"
    model.generateAndSaveAlignments(outFile)

   
        
