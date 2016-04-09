CS 447, Fall 2015
Homework 3

This directory contains 10 files:

   (1)   README.txt:          This file
   (2)   hw3.pdf:             PDF handout with the description of the assignment

Part 1: Writing a Context-Free Grammar
   Code:
   (3)  hw3_nltkcfg.py:       Python module for parsing using CFG using NLTK and your grammar (provided code)

   Data:
   (4)  sentences.txt:        The list of sentences that are parsed by hw3_nltkcfg.py (provided data)
   (5)  mygrammar.cfg:        The grammar being used by the parsing in hw3_nltkcfg.py (your solution)

   Output:
   (6)  hw3_cfg_out.txt:      Successful parse trees in tabbed, bracketed format, generated from hw3_nltkcfg.py (generated file)

Part 2: Parsing with Probabilistic Context Free Grammars
    Code:
    (7)  hw3_pcfg.py:         Python module for parsing using CKY (your solution)
    (8)  hw3_pcfg_test.py:    Python module for evaluating your hw3_pcfg.py solution (provided code)

    Data:
    (9)  toygrammar.cfg:      The grammar being used for the parsing in hw3_pcfg.py (provided data)
    (10) pcfg_test_gold.txt:  The set of gold parses that hw3_pcfg_test.py uses to evaluate your solution (provided data)