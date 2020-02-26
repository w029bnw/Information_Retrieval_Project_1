
'''
query processing

'''
import util
import norvig_spell
import cran
import index as inverted_ind
from index import IndexItem
from index import Posting
import pickle
import unittest
import cranqry
import doc as d
import numpy as np

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
        query_terms = self.preprocessing()
        docs = []
        docs_empty = True
        for word in query_terms:
            index_item = self.index.find(word)
            
            if(index_item != None):
                postings = index_item.sorted_postings
                
                if postings != []:
                    # If this is the first word being checked in the index we add
                    # all of the docIDs to our list of relevant documents
                    if docs_empty is True:
                        docs = postings
                        
                        docs_empty = False
                     
                    # If this is not the first word being checked in the index,
                    # we need to compare lists and store a list of docIDs that 
                    # appear in both the current posting and the existing list of
                    # docIDs. This creates our intersection of relevant docIDs
                    # for the tokens from the query
                    else:
                        if docs != []:
                            docs = set(docs).intersection(set(postings))
                         
                        # No more shared documents exist, return
                        else:
                            return []
                        
            # If the term doesn't exist in the document collection, then
            # there won't be a list of shared relevant documents.
            else:
                return []
                    
        # Sort docs if they exist
        if list(docs) != []:
            list(docs).sort()
                    
        return list(docs)              

    def vectorQuery(self, k):
        ''' vector query processing, using the cosine similarity. '''
        query_terms = self.preprocessing()
        relevant_docs = []
        
        # Start by creating a comprehensive list of all the possible relevant
        # documents in the collection
        for word in query_terms:
            index_item = self.index.find(word)
            
            if index_item != None:
                postings = index_item.posting
                
                for doc in postings:
                    if doc not in relevant_docs:
                        relevant_docs.append(doc)
        
        relevant_docs.sort()
                        
        # Calculate the weight of each term for each possible relevant document
        tf_idf_matrix = {}
        for word in query_terms:
            tf_idf = []
            index_item = self.index.find(word)
            
            if index_item != None:
                postings = index_item.posting
                for doc in relevant_docs:
                    if doc in postings:
                        score = postings[doc].term_freq(self.index.docLength[doc]) * self.index.idf(word)
                    else:
                        score = 0
                        
                    tf_idf.append(score)  
                    
            else:
                for doc in relevant_docs:
                    score = 0
                    tf_idf.append(score)
                    
            tf_idf_matrix.update({word : tf_idf})
                    
         # Calculate the similarity between each document
         for i in range(len(relevant_docs)):
             for j in range(len(relevant_docs)):
                 
                 

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
    def test_boolean_query_with_results(self):
        inverted_index = inverted_ind.InvertedIndex()
        doc1 = d.Document('1','temp','me','Dogs are friendly.')
        doc2 = d.Document('2','temp','me','Cats are friendly.')
        doc_list = [doc1, doc2]
        
        for doc in doc_list:
            inverted_index.indexDoc(doc)
        
        inverted_index.sort()
        
        query = "friendly"
        query_processor = QueryProcessor(query, inverted_index, doc_list)
        relevant_docs = query_processor.booleanQuery()
        
        assert relevant_docs == [1,2]
        
    def test_boolean_query_without_results(self):
        inverted_index = inverted_ind.InvertedIndex()
        doc1 = d.Document('1','temp','me','Dogs are friendly.')
        doc2 = d.Document('2','temp','me','Cats are friendly.')
        doc_list = [doc1, doc2]
        
        for doc in doc_list:
            inverted_index.indexDoc(doc)
        
        inverted_index.sort()
        
        query = "dogs and cats"
        query_processor = QueryProcessor(query, inverted_index, doc_list)
        relevant_docs = query_processor.booleanQuery()
        
        assert relevant_docs == []
#        
#    def test_vector_query(self):
        

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
    
    filename = 'output.p'
    inverted_index = inverted_ind.InvertedIndex()
    inverted_index.load(filename)
    
# TODO: Current code is for testing - be sure to replace this with code
# that can accept input query strings as defined in the project document
    for query in queries:
        query_processor = QueryProcessor(queries[query].text, inverted_index, collection)
#        temp = query_processor.booleanQuery()
        temp = query_processor.vectorQuery(3)
        
    
if __name__ == '__main__':
    #unittest.main()
    query()
