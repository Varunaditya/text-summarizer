from nltk import word_tokenize
from nltk.corpus import wordnet as wn
from collections import defaultdict, Counter
import networkx as nx
import matplotlib.pyplot as plt
import sys


def readFromFile(file):
	#reads sentences from the file. The sentences must be seperated by a new line character.
	file = open(file,'r')
	sentence = list()
	data = file.readline()
	while(data):
		sentence.append(data.strip())
		data = file.readline()
	return ' '.join(sentence), sentence

def fromWordNet(sentence):
	#gets the sentences and run them against the data from wordnet to get hypernyms/hyponyms and synonyms/antonyms
	final = defaultdict(lambda : 'NaN')
	tokens = word_tokenize(sentence) #to tokenize the sentences
	wordCount = Counter(tokens)
	for i in tokens:
		output = list()
		synsetList = (wn.synsets(i)) #gets the list of sysnsets for a particular word
		if synsetList:
			output.extend(synsetList)
			#checking if the synsets have hyponyms or hypenyms
			for j in synsetList:
				haveHypernyms = [j.hypernyms()]
				if len(haveHypernyms[0]):
					output.append(haveHypernyms[0][0])
				haveHyponyms = [j.hyponyms()]
				if len(haveHyponyms[0]):
					output.append(haveHyponyms[0][0])
		if output:
			final[i] = output
	#returns data extracted from wordnet and the tokens as well to keep a count of words present in the sentence
	return final, tokens 

def createGraph(final):
	#uses the networkx library to connect the words that are similar in sense of synsets, hypernyms/hyponyms and synonyms/antonyms
	word_keys = [i for i in final.keys()]
	i = 0
	#this method create two graphs
	#graph: for representation purposes, only has necessary edges connected in order to have a neat representation
	#graph1: for bulding lexical chains, has all the possible edges connected
	graph = nx.Graph()
	graph1 = nx.Graph()
	while(i < len(word_keys)):
		for j in range (i+1,len(word_keys)):
			score = len(set(final[word_keys[i]]).intersection(set(final[word_keys[j]])))
			if score:
				graph.add_node(word_keys[i])
				graph.add_node(word_keys[j])
				graph1.add_edge(word_keys[i],word_keys[j])
				if not len(set(graph.neighbors(word_keys[i])).intersection(set(graph.neighbors(word_keys[j])))):
					graph.add_edge(word_keys[i],word_keys[j])
			else:
				graph.add_node(word_keys[i])
				graph1.add_node(word_keys[i])
		i += 1
	return graph,graph1

def drawGraph(graph, wordCount):
	#this method plots the graph and saves it in a png file
	labels = defaultdict(lambda : 0)
	for i in graph.nodes():
		labels[i] = i+'('+str(wordCount[i])+')'
	plt.figure(figsize=(20,20))
	nx.draw_networkx(graph,font_size=25,alpha=0.2, labels=labels, width=3)
	plt.savefig('lexicalChains.png')

def initiateLexicalChains(graph1):
	#one of the two methods to create lexical chains
	#takes all the nodes and relevant neighors from graph1 object and stores in a dictionary
	#in order to make it easier for comparison
	first = {}
	for node in graph1.nodes():
		temp = graph1.neighbors(node)
		temp.append(node)
		temp = sorted(temp)
		first.update({node : temp})
	second = createLexicalChains(first)
	return second

def createLexicalChains(first):
	#second of the two methods used to create lexical chains
	#
	i = 0
	second = {}
	chainNumber = 1
	flag = 1
	values = list(first.values())
	seenIndex = list()
	seenValues = []
	while(i < len(values) - 1):
		temp = list()
		for j in range(i+1,len(values)):
			inCommon = set(values[i]).intersection(set(values[j]))
			# diff1 = set(values[i]).difference(set(values[j]))
			# diff2 = set(values[j]).difference(set(values[i]))
			if inCommon and (i and j not in seenIndex):
				flag = 1
				seenIndex.append(i)
				seenIndex.append(j)
				temp.extend(values[i])
				temp.extend(values[j])
				seenValues.extend(temp)
			else:
				flag = 0
				if i not in seenIndex and list(sorted(values[i])) not in second.values(): 
					seenIndex.append(i)
					seenValues.extend(values[i])
					second.update({chainNumber : values[i]})
					chainNumber += 1
		if flag and not len(set(temp).intersection(set(seenValues))):
			second.update({chainNumber : list(set(temp))})
			chainNumber += 1
		i += 1
	return second

def printLexicalChains(second, wordCount):
	secondCopy = dict(second)
	for i in second.keys():
		temp = list()
		for j in secondCopy[i]:
			temp.append(j + '(' + str(wordCount[j]) + ')')
		temp = ', '.join(temp)
		secondCopy.update({i : temp})
	for i,value in enumerate(secondCopy.keys()):
		print('Chain ',i+1,': ', secondCopy[value])
	print('\n','*'*10,'The representation of lexical chains on a graph was stored in Jadwal - Lexical Chains.png','*'*10)
	
def summarizeText(second, lineWiseSentence):
	#creating a list of pronouns to keep track of them while creating summary.
	pronouns = ['I','you','he','she','it','they','we','me','you','him','her','it','us','them']
	#targetIndex holds the index that has the longest chain while wordsToLookFor holds the words that are part of that chain
	targetIndex = sorted(second.items(), key = lambda x : -len(x[1]))[0][0]
	wordsToLookFor = second[targetIndex]
	#output is a list that holds all the sentences part of the summary
	output = list()
	#previous line stores the sentence that was traversed one traversal back in order to append it to the output if a pronoun is seen
	previousLine = str()
	for line in lineWiseSentence:
		previousLine = line
		if len(set(line.split()).intersection(set(wordsToLookFor))): #checking if the current line has a word from the lexical chain
			if len(set([k.lower() for k in line.split()]).intersection(set(pronouns))): 
				output.append(previousLine) #handling pronouns by inserting the previous sentence from where the pronoun was seen, whetehre the previous line matches or not
			output.append(line)
	print('\n','*'*10,'The summary was stored in summary.txt','*'*10)
	file = open('summary.txt','w')
	file.write(' '.join(set(output)))
	file.close()

def main():
	if len(sys.argv) == 2:
		fileName = sys.argv[1]
		proceed = True
	else:
		print('Usage: python textSummarizer.py <file with sentences to be summarized>')
		sys.exit()
	if proceed:
		sentence, lineWiseSentence = readFromFile(fileName)
		final, tokens = fromWordNet(sentence)
		wordCount = Counter(tokens)
		graph, graph1 = createGraph(final)
		drawGraph(graph, wordCount)
		second = initiateLexicalChains(graph)
		printLexicalChains(second, wordCount)
		summarizeText(second, lineWiseSentence)

if __name__ == '__main__':
	main()