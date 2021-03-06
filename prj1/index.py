'''

Index structure:
    The Index class contains a list of IndexItems, stored in a dictionary type for easier access
    each IndexItem contains the term and a set of PostingItems
    each PostingItem contains a document ID and a list of positions that the term occurs
    
'''

import util
import doc as d
import cran
import unittest
import math
import pickle
import sys
import nltk

class Posting:
    def __init__(self, docID):
        self.docID = docID
        self.positions = []

    def append(self, pos):
        self.positions.append(pos)

    def sort(self):
        ''' sort positions'''
        self.positions.sort()
 
    def merge(self, positions):
        self.positions.extend(positions)

    def term_freq(self, doc_length):
        ''' return the term frequency in the document'''
#        return (len(self.positions)/doc_length)
        return len(self.positions)


class IndexItem:
    def __init__(self, term):
        self.term = term
        self.posting = {} #postings are stored in a python dict for easier index building
        self.sorted_postings= [] # may sort them by docID for easier query processing

    def add(self, docid, pos):
        ''' add a posting'''
        if int(docid) not in self.posting.keys():
            self.posting[docid] = Posting(docid)
        self.posting[docid].append(pos)

    def sort(self):
        ''' sort by document ID for more efficient merging. For each document also sort the positions'''
        for item in sorted(self.posting.keys()):
            self.sorted_postings.append(item)


class InvertedIndex:

    def __init__(self):
        self.items = [] # list of IndexItems
        self.nDocs = 0  # the number of indexed documents
        self.docLength = {} # The length of each document

    def indexDoc(self, doc): # indexing a Document object
        ''' indexing a document, using the simple SPIMI algorithm, but no need 
        to store blocks due to the small collection we are handling. 
        Using save/load the whole index instead'''
        
        # Tokenize document, remove stop words, normalize, and stem
        tokens = util.preprocess(doc.body)
        
        # Add tokens to dictionary 
        token_counter = 0
        for token in tokens:
            found = False
            for item in self.items:
                if token == item.term:
                    found = True
                    break
                    
            # If token not stored in dictionary already, then add it and create
            # a posting
            if found == False:
                item = IndexItem(token)
                item.add(int(doc.docID), token_counter)
                self.items.append(item)
                
            # If token is already in dictionary, update posting to include
            # new document(s) and position(s)
            else:
                for index in self.items:
                    if index.term == token:
                        index.add(int(doc.docID), token_counter)
            token_counter += 1
                        
        self.nDocs += 1
        self.docLength.update({self.nDocs : len(doc.body.split())})
        
    def sort(self):
        ''' sort all posting lists by docID'''
        for item in self.items:
            item.sort()

    def find(self, term):
        for item in self.items:
            if item.term == term:
                return item
        
        # If the term doesn't exist return an empty object
        return None
            

    def save(self, filename):
        ''' save to disk'''
        serial_data=open(filename, 'wb')
        pickle.dump([self.items, self.nDocs, self.docLength], serial_data, -1)
        serial_data.close()

    def load(self, filename):
        ''' load from disk'''
        serial_data= open(filename, 'rb')
        data = pickle.load(serial_data)
        serial_data.close()
        
        self.items = data[0]
        self.nDocs = data[1]
        self.docLength = data[2]

    def idf(self, term):
        ''' compute the inverted document frequency for a given term'''
        index_item = self.find(term)
        if (self.nDocs/len(index_item.sorted_postings)) > 0:
            idf = math.log(self.nDocs/len(index_item.sorted_postings))
        else:
            idf = 0
        return idf

class test(unittest.TestCase):
    ''' test your code thoroughly. put the testing cases here'''

# Test stemming used to make sure it's behaving as expected
    def test_short_strings(self):
        assert util.stemming("y's") == "y"
        
    def test_english_stemming(self):
        assert util.stemming("having") == "have"
        
# Test that stopwords are being removed as expected
    def test_stopword_removal(self):
        tokens = ['to', 'sleep', 'perchance', 'to', 'dream','...']
        processed_tokens = []
        for term in tokens:
            if(util.isStopWord(term) == False):
                processed_tokens.append(term)
                
        assert 'to' not in processed_tokens
        
# Test that terms are added to the dictionary and their postings are updated as
# expected
    def test_new_dictionary_terms(self):
        inverted_index = InvertedIndex()
        doc = d.Document('1','temp','me',"This is a test. Test, test, test...")
        
        inverted_index.indexDoc(doc)
        
        assert len(inverted_index.items) != 0
        
    def test_posting_updates(self):
        inverted_index = InvertedIndex()
        doc = d.Document('1','temp','me',"This is a test. Test, test, test...")
        inverted_index.indexDoc(doc)
        
        assert inverted_index.items[0].posting[1].term_freq(inverted_index.docLength[1]) == (4/7)

# Test that sorting happens as expected
    def test_index_sorting(self):
        inverted_index = InvertedIndex()
        doc1 = d.Document('1','temp','me','Hello, World!')
        doc2 = d.Document('2','temp','me','This is my sixth test.')
        doc3 = d.Document('3','temp','me','I hope you enjoy this test.')
        doc_list = [doc1, doc3, doc2]
        
        for doc in doc_list:
            inverted_index.indexDoc(doc)
        
        inverted_index.sort()
        
        assert inverted_index.items[0].posting[1].docID == 1
        assert inverted_index.items[4].posting[2].docID == 2
        assert inverted_index.items[4].posting[3].docID == 3
        
## Test that serialization happens as expected and that the index can be saved
## and loaded

    def test_save_and_load(self):
        inverted_index = InvertedIndex()
        doc = d.Document('1','temp','me',"This is a test. Test, test, test...")
        inverted_index.indexDoc(doc)
        inverted_index.save('output.p')
        
        inverted_index_new = InvertedIndex()
        inverted_index_new.load('output.p')
        assert inverted_index.items[0].term == inverted_index_new.items[0].term

def indexingCranfield(doc_filename, index_filename):
    
    # Load cran.all and create a cran_file object to store the document info
    cran_file = cran.CranFile(doc_filename)
        
    inverted_index = InvertedIndex()
    for doc in cran_file.docs:
        inverted_index.indexDoc(doc)
         
    # Sort the index by docID
    inverted_index.sort()
    
    # Save the index
    inverted_index.save(index_filename)

    print('Done')

if __name__ == '__main__':
#    unittest.main()
#    indexingCranfield('cran.all', 'output.p')
    indexingCranfield(sys.argv[1], sys.argv[2])