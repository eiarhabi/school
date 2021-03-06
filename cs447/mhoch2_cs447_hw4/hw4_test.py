import sys, os, math, codecs, hw4_translate

# A class to test your IBMModel1's alignments
class IBMModel1Tester:
    def __init__(self, filename):
        self.english = []
        self.spanish = []
        self.alignments = []
        self.initialize(filename);

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
                self.english.append(tTokenized)
            elif i == 1:           
                fTokenized = s.split()
                self.spanish.append(fTokenized)
            elif i == 2:           
                self.alignments.append([int(k) for k in s.split()])
            else:
                i = -1
                j += 1
            i +=1
        file.close()
        return

    # Evaluate an IBMModel1
    def test(self, model):
        total = 0.0
        matched = 0.0
        for i in range(len(self.english)):
            total += len(self.spanish[i])
            modelAlign = model.align(self.spanish[i], self.english[i])
            for j in range(len(modelAlign)):
                if modelAlign[j] == self.alignments[i][j]:
                    matched += 1.0
        acc = 100*matched/total
        print "Your model's alignment accuracy compared to TA implementation: "+str(acc)+"%"
    

if __name__ == "__main__":
    # Initialize model
    model = hw4_translate.IBMModel1('eng-spa_small.txt')
    # Train model
    model.trainUsingEM(20, .5, False);
    # Check model
    tester = IBMModel1Tester('reference_alignments.txt')
    tester.test(model)
    

