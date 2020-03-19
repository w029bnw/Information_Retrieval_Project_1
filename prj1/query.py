'''
query processing

'''
import util
import norvig_spell
import cran
import index as inverted_ind
from index import IndexItem
from index import Posting
import unittest
import cranqry
import doc as d
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import operator
import sys
import random
import batch_eval

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
        
        # Add the query to the inverted_index as a document
        n = self.index.nDocs + 1
        query_doc = d.Document(str(n),'temp','me', self.raw_query)
        self.index.indexDoc(query_doc)
        self.index.sort()
        
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
        tf_idf_matrix = np.empty((len(query_terms),len(relevant_docs)))
        row = 0
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
                    
            tf_idf_matrix[row] = tf_idf
            row += 1
                    
        # Calculate the similarity between each document and the query document
        similarities = {}
        for i in range(len(tf_idf_matrix[0])-1):         
            similarity = cosine_similarity([tf_idf_matrix[:,i]], [tf_idf_matrix[:,-1]])
            similarities.update({relevant_docs[i] : similarity[0][0]})
            
        # Sort the dictionary by values
        sorted_similarities = sorted(similarities.items(), key=operator.itemgetter(1), reverse=True)
        
        # Retrieve k results and return
        k_pairs = []
        for x in range(k):
            k_pairs.append(sorted_similarities[x])
            
        return k_pairs


class test(unittest.TestCase):
    ''' test your code thoroughly. put the testing cases here'''
    
    # Test that the spell check works for both technical and non technical words
    def test_spellcheck(self):
        word = 'retangulor'
        assert norvig_spell.correction(word) == 'rectangular'
        
    def test_spellcheck_technical(self):
        word = 'magntohydodynamic'
        assert norvig_spell.correction(word) == 'magnetohydrodynamic'
        
    # Test boolean query model
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
        
    # Test vector query model
    def test_vector_query_1(self):
        inverted_index = inverted_ind.InvertedIndex()
        doc1 = d.Document('1','temp','me','Dogs are friendly and social.')
        doc2 = d.Document('2','temp','me','Cats can be friendly, but are often aloof.')
        doc3 = d.Document('3','temp','me','Owners should consider which type of personality will fit their own personality the best.')
        doc_list = [doc1, doc2, doc3]
        
        for doc in doc_list:
            inverted_index.indexDoc(doc)
            
        inverted_index.sort()
        
        query = "Are dogs friendly?"
        query_processor = QueryProcessor(query, inverted_index, doc_list)
        relevant_docs = query_processor.vectorQuery(2)
        
        assert relevant_docs[0][0] == 1
        assert relevant_docs[1][0] == 2
        
    def test_vector_query_2(self):
        inverted_index = inverted_ind.InvertedIndex()
        doc1 = d.Document('1','temp','me','Dogs are friendly and social.')
        doc2 = d.Document('2','temp','me','Cats can be friendly, but are often aloof.')
        doc3 = d.Document('3','temp','me','Owners should consider which type of personality will fit their own personality best when choosing whether to own a cat or dog.')
        doc_list = [doc1, doc2, doc3]
        
        for doc in doc_list:
            inverted_index.indexDoc(doc)
            
        inverted_index.sort()

        query = "How do owners decide whether to own a cat or a dog?"   
        query_processor = QueryProcessor(query, inverted_index, doc_list)
        relevant_docs = query_processor.vectorQuery(3)
        
        assert relevant_docs[0][0] == 3
        assert relevant_docs[1][1] == relevant_docs[2][1]
        
    # Test the accuracy of the cosine similarity calculations
    def test_cosine_similarity_same_vectors(self):
        # Using only a single word across 2 strings
        a = np.matrix([1])
        b = np.matrix([1])
        
        np.transpose(a)
        np.transpose(b)
        
        similarity = cosine_similarity(a,b)
        
        assert similarity[0][0] == 1
        
    def test_cosine_similarity_different_vectors(self):
        # Using only a single word across 2 strings
        a = np.matrix([0])
        b = np.matrix([1])
        
        np.transpose(a)
        np.transpose(b)

        similarity = cosine_similarity(a,b)
        
        assert similarity[0][0] == 0
        
def query(index_filename, mode, query_filename, qid_or_n):
    ''' the main query processing program, using QueryProcessor'''
    
    # Load document collection, inverted_index file, and the query file
    filename = 'cran.all'
    collection = cran.CranFile(filename)
    
    inverted_index = inverted_ind.InvertedIndex()
    inverted_index.load(index_filename)
    
    queries = cranqry.loadCranQry(query_filename)
    
    # Boolean query
    if mode == 0:
        query = queries[qid_or_n]
        query_processor = QueryProcessor(query.text, inverted_index, collection)
        print(query_processor.booleanQuery())
       
    # Vector Query
    elif mode == 1:
        query = queries[qid_or_n]
        query_processor = QueryProcessor(query.text, inverted_index, collection)
        print(query_processor.vectorQuery(3))
      
    # Batch Evaluation
    elif mode == 2:
        n_queries = random.sample(list(queries.values()), int(qid_or_n))
        query_processor = QueryProcessor('', inverted_index, collection)
        b_time, v_time = batch_eval.time_evaluation(n_queries, query_processor)
        
        print('Avg Boolean Query Processing Time: %4.4f Avg Vector Query Processing Time: %4.4f' % (b_time, v_time))
        
if __name__ == '__main__':
#    unittest.main()
#    query('output.p', 0, 'query.text', '201') # Boolean
#    query('output.p', 1, 'query.text', '201') # Vector
#    query('output.p', 2, 'query.text', 20) # Batch Eval
    
    query(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])