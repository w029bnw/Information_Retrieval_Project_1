
'''
query processing

'''
import util
import norvig_spell
import cran
import index as inverted_ind
import pickle
import unittest
import cranqry

class QueryProcessor:

    def __init__(self, query, index, collection):
        ''' index is the inverted index; collection is the document collection'''
        self.raw_query = query
        self.index = index
        self.docs = collection

    def preprocessing(self):
        ''' apply the same preprocessing steps used by indexing,
            also use the provided spelling corrector. Note that
            spelling corrector should be applied before stopword
            removal and stemming (why?)'''
        
        # Spell check words in the query
        spell_checked_words = []
        words = util.tokenize(self.raw_query)
        for word in words:
            spell_checked_words.append(norvig_spell.correction(word))
            
        # Now remove stopwords and stem
        processed_words = []
        for word in spell_checked_words:
            if util.isStopWord(word) is True:
                continue
            else:
                stemmed_word = util.stemming(word)
                processed_words.append(stemmed_word)
                
        return processed_words


    def booleanQuery(self):
        ''' boolean query processing; note that a query like "A B C" is 
        transformed to "A AND B AND C" for retrieving posting lists and merge 
        them'''
        query_terms = preprocessing()
        docs = []
        for word in query_terms:
            index_item = self.index.find(word)
            postings = index_item.sorted_postings
            
            if postings != []:
                # If this is the first word being checked in the index we add
                # all of the docIDs to our list of relevant documents
                if docs == []:
                    for doc in postings:
                        docs.append(doc)
                 
                # If this is not the first word being checked in the index,
                # we need to compare lists and store a list of docIDs that 
                # appear in both the current posting and the existing list of
                # docIDs. This creates our intersection of relevant docIDs
                # for the tokens from the query
                else:
                    temp = []
                    for doc in postings:
                        if doc in docs:
                            temp.append(doc)
                            
                    # Set the list of doc IDs to the intersected list
                    docs = temp
                    
                return docs.sort()                 

    def vectorQuery(self, k):
        ''' vector query processing, using the cosine similarity. '''
        #ToDo: return top k pairs of (docID, similarity), ranked by their cosine similarity with the query in the descending order
        # You can use term frequency or TFIDF to construct the vectors



class test(unittest.TestCase):
    ''' test your code thoroughly. put the testing cases here'''
    
# Test that the spell check works for both technical and non technical words
    def test_spellcheck(self):
        word = 'retangulor'
        assert norvig_spell.correction(word) == 'rectangular'
        
    def test_spellcheck_technical(self):
        word = 'magntohydodynamic'
        assert norvig_spell.correction(word) == 'magnetohydrodynamic'
        
#    def test_boolean_query(self):
#        
#    def test_vector_query(self):
        
    print('Pass')

def query():
    ''' the main query processing program, using QueryProcessor'''

    # ToDo: the commandline usage: "echo query_string | python query.py index_file processing_algorithm"
    # processing_algorithm: 0 for booleanQuery and 1 for vectorQuery
    # for booleanQuery, the program will print the total number of documents and the list of docuement IDs
    # for vectorQuery, the program will output the top 3 most similar documents
    
    filename = 'query.text'
    queries = cranqry.loadCranQry(filename)
    
    filename = 'cran.all'
    collection = cran.CranFile(filename)
    
# TODO: Load the saved inverted index object
    filename = 'serialData'
    inverted_index = inverted_ind.InvertedIndex()
    inverted_index.load(filename)
    
# TODO: Current code is for testing - be sure to replace this with code
# that can accept input query strings as defined in the project document
    for query in queries.docs:
        query_processor = QueryProcessor(query, index, collection)
        
    
if __name__ == '__main__':
    unittest.main()
    #query()
