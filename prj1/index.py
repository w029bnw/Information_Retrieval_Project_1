'''

Index structure:

    The Index class contains a list of IndexItems, stored in a dictionary type for easier access

    each IndexItem contains the term and a set of PostingItems

    each PostingItem contains a document ID and a list of positions that the term occurs

'''
import util
import doc as d
import sys
import cran
import unittest

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

    def term_freq(self):
        ''' return the term frequency in the document'''
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


    def indexDoc(self, doc): # indexing a Document object
        ''' indexing a document, using the simple SPIMI algorithm, but no need 
        to store blocks due to the small collection we are handling. 
        Using save/load the whole index instead'''
        
        # Tokenize document, remove stop words, normalize, and stem
        tokens = util.tokenize(doc)
        
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
        
    def sort(self):
        ''' sort all posting lists by docID'''
        for item in self.items:
            item.sort()

    def find(self, term):
        return self.items[term]

    def save(self, filename):
        ''' save to disk'''
        f = open(filename,'w')
        f.write(self.indexDoc)
        f.close()

    def load(self, filename):
        ''' load from disk'''
        f = open(filename, 'r')
        docs = f.readlines()
        f.close()

    def idf(self, term):
        ''' compute the inverted document frequency for a given term'''
        #ToDo: return the IDF of the term


class test(unittest.TestCase):
    ''' test your code thoroughly. put the testing cases here'''

# Test stemming used to make sure it's behaving as expected
    def test_short_strings(self):
        assert util.stemming("y's") == "y"
        
    def test_english_stemming(self):
        assert util.stemming("having") == "have"
        
# Test that stopwords are being removed as expected
    def test_stopword_removal(self):
        tokens = ['to', 'sleep', 'perchance', 'to', 'dream']
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
        
        assert inverted_index.items[0].posting[1].term_freq() == 4

# Test that sorting happens as expected
    def test_sorting(self):
        
        
# Test that serialization happens as expected and that the index can be saved
# and loaded
    def test_saves(self):
        
    def test_loads(self):
        
    print ('Pass')

def indexingCranfield():
    #ToDo: indexing the Cranfield dataset and save the index to a file
    # command line usage: "python index.py cran.all index_file"
    # the index is saved to index_file
    
    # Load cran.all and create a cran_file object to store the document info
    filename = 'cran.all'
    cran_file = cran.CranFile(filename)
        
    inverted_index = InvertedIndex()
    for doc in cran_file.docs:
        inverted_index.indexDoc(doc)
         
    # Sort the index by docID
    inverted_index.items.sort()

    print('Done')

if __name__ == '__main__':
    unittest.main()
    #indexingCranfield()
