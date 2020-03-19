'''
a program for evaluating the quality of search algorithms using the vector model

it runs over all queries in query.text and get the top 10 results,
and then qrels.text is used to compute the NDCG metric

usage:
    python batch_eval.py index_file query.text qrels.text n

    output is the average NDCG over all the queries for boolean model and vector model respectively.
	also compute the p-value of the two ranking results. 
'''
import metrics
import time
import query as q
import sys
import index as inverted_ind
import cranqry
import random
from scipy import stats as stats
import numpy as np
import cran
from index import IndexItem
from index import Posting


def eval(index_filename, query_filename, relevant_filename, n):
    '''Evaluates performance of boolean and vector query models by determining 
    whether returned relevant documents match expected results as defined in
    qrels.text. The results are scored using NDCG and the scores are compared
    statistically using T-Tests and Wilcoxon Tests.'''
    
    # Load necessary files
    filename = 'cran.all'
    collection = cran.CranFile(filename)
    
    inverted_index = inverted_ind.InvertedIndex()
    inverted_index.load(index_filename)
    
    queries = cranqry.loadCranQry(query_filename)
    n_queries = random.sample(list(queries.values()), n)
    
    f = open(relevant_filename, 'r')
    data = f.readlines()
    f.close()
    
    # Puts the qrels data into a dictionary such that there is easy access
    # to a complete list of relevant documents for a given query. This
    # makes scoring easier
    qrels = {}
    qrels_list = []
    i = 0
    for line in data:
        line = line.split()
        if int(line[0]) not in qrels.keys():
            i = int(line[0])
            if qrels == {}:
                qrels_list.append(int(line[1]))
                qrels.update({i : qrels_list})
            
            else:
                qrels_list = []
                qrels_list.append(int(line[1]))
                qrels.update({i : qrels_list})
                
        else:
            qrels_list.append(int(line[1]))
            
    # Evaluate models
    avg_score_boolean = 0
    avg_score_vector = 0
    boolean_scores = []
    vector_scores = []
    for query in n_queries:
        query_processor = q.QueryProcessor(query.text, inverted_index, collection)
        results_boolean = query_processor.booleanQuery()
        
        # For instances where there are less than 3 relevant docs recorded in
        # qrels, we will adjust the number of returned relevant documents
        # to match the number in qrels. Otherwise an indexing error occurs
        if len(qrels[int(query.qid)]) >= 3:
            results = query_processor.vectorQuery(3)
        else:
            results = query_processor.vectorQuery(len(qrels[int(query.qid)]))
        
        # Pull the doc IDs from the vector results
        results_vector = []
        for result in results:
            results_vector.append(result[0])
            
        # Score results using NDCG scoring
        score_boolean = metrics.ndcg_score(qrels[int(query.qid)], results_boolean)       
        score_vector = metrics.ndcg_score(qrels[int(query.qid)], results_vector)
            
        boolean_scores.append(score_boolean)
        vector_scores.append(score_vector)
        
        avg_score_boolean += score_boolean
        avg_score_vector += score_vector
        
    # Take the average of the scores
    boolean_score = avg_score_boolean / n
    vector_score = avg_score_vector / n
    
    # Run T-Tests and Wilcoxon Tests on the results
    t_stat, t_p = stats.ttest_ind(boolean_scores, vector_scores)
    w_stat, w_p = stats.wilcoxon(boolean_scores, vector_scores)
    
    print("Boolean Score: %4.4f Vector Score: %4.4f T-Test p: %4.4f, Wilcoxon p: %4.4f" % (boolean_score, vector_score, t_p, w_p))
    
def time_evaluation(queries, query_processor):
    ''' Used to evaluate the processing time of both boolean and vector models.'''

    total_time_boolean = 0
    total_time_vector = 0
        
    for query in queries:
        query_processor.raw_query = query.text
            
        # Time boolean model
        time_start_boolean = time.clock()
        query_processor.booleanQuery()
        time_stop_boolean = time.clock()
        time_boolean = time_stop_boolean - time_start_boolean
        total_time_boolean += time_boolean
        
        # Time vector model
        time_start_vector = time.clock()
        query_processor.vectorQuery(3)
        time_stop_vector = time.clock()
        time_vector = time_stop_vector - time_start_vector
        total_time_vector += time_vector
        
    return (total_time_boolean, total_time_vector)

if __name__ == '__main__':
#    eval('output.p', 'query.text', 'corrected_qrels.text', 50)
    eval(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
