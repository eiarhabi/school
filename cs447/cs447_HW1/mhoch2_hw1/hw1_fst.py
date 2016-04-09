from fst import *

# here are some predefined character sets that might come in handy.
# you can define your own
AZ = set("abcdefghijklmnopqrstuvwxyz")
VOWS = set("aeiou")
CONS = set("bcdfghjklmnprstvwxz")
E = set("e")
U = set("u")
I = set("i")
rule2 = set("nptr")

# Implement your solution here
def buildFST():
    print "Your task is to implement a better FST in the buildFST() function, using the methods described here"
    print "You may define additional methods in this module (hw1_fst.py) as desired"
    #
    # The states (you need to add more)
    # ---------------------------------------
    # 
    f = FST("q0") # q0 is the initial (non-accepting) state
    f.addState("q1") # a non-accepting state

    f.addState("E?")
    f.addState("E")
    f.addState("lastE?")
    f.addState("exception")
    f.addState("u-handler")
    f.addState("end?")

    f.addState("rule2")
    f.addState("return")
    f.addState("rule3")
    f.addState("end3?")

    f.addState("q_ing") # a non-accepting state
    f.addState("q_EOW", True) # an accepting state (you shouldn't need any additional accepting states)

    #
    # The transitions (you need to add more):
    # ---------------------------------------
    # transduce every element in this set to itself: 
    f.addSetTransition("q0", AZ, "q1")
    
    f.addSetTransition("q1", AZ-(U|CONS|VOWS), "q1")
   
    f.addSetTransition("q1", CONS, "E?")
    f.addSetTransition("q1", VOWS-(E|U), "rule2")
    f.addSetTransition("q1", U, "u-handler")
    f.addTransition("q1", "i", "y", "rule3")
    f.addSetTransition("q1", E, "exception")

    # RULE 1 code
    f.addSetTransition("E?", U|CONS, "E?")
    f.addSetTransition("E?", AZ-(U|CONS|E), "q1")
    f.addTransition("E?", "", "ing", "q_EOW")


    f.addEpsilonTransition("E?", "lastE?")
    f.addTransition("lastE?", "e", "", "q_ing")# Will kill if not last
    f.addTransition("lastE?", "e", "e", "end?")
    f.addSetTransition("end?", AZ, "q1")

    # RULE 2
    f.addTransition("rule2", "n","nn", "q_ing")
    f.addTransition("rule2", "p","pp", "q_ing")
    f.addTransition("rule2", "t","tt", "q_ing")
    f.addTransition("rule2", "r","rr", "q_ing")
    f.addSetTransition("rule2", AZ-(rule2|CONS), "q1")
    f.addSetTransition("rule2", CONS-rule2, "E?")
    f.addSetTransition("rule2", rule2, "return")#if not last char return to q1
    f.addSetEpsilonTransition("return", AZ, "q1")

    #exception
    f.addTransition("exception", "p", "pp", "q_ing")
    f.addTransition("exception", "t", "tt", "q_ing")
    f.addSetTransition("exception", set("pt"), "return")
    f.addSetTransition("exception", U|CONS-set("pt"), "E?")
    f.addSetTransition("exception", AZ-(U|CONS|E), "q1")

    #u-handler
    f.addTransition("u-handler", "e", "", "q_ing")
    f.addEpsilonTransition("u-handler", "rule2")

    # RULE 3
    f.addTransition("rule3", "e", "", "q_ing")

    
    
    # map the empty string to ing: 
    f.addTransition("q_ing", "", "ing", "q_EOW")
    f.addTransition("q1", "", "ing", "q_EOW")

    # Return your completed FST
    return f
    

if __name__ == "__main__":
    # Pass in the input file as an argument
    if len(sys.argv) < 2:
	print "This script must be given the name of a file containing verbs as an argument"
	quit()
    else:
        file = sys.argv[1]
    #endif

    # Construct an FST for translating verb forms 
    # (Currently constructs a rudimentary, buggy FST; your task is to implement a better one.
    f = buildFST()
    # Print out the FST translations of the input file
    f.parseInputFile(file)
