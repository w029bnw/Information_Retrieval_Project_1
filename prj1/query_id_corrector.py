''' 

Script to correctly label query ids such that the query id given in qrels.text
matches the query id in query.text. 

A new file is written (corrected_qrels.text) to replace the use of qrels.text
when comparing relevance of query results.

'''

import cranqry

# Load and open both the query file and the qrels file
query_file = cranqry.loadCranQry('query.text')

f = open('qrels.text', 'r')
data = f.readlines()
f.close()

# Get just the qids for each query contained in the query file
qids = []
for query in query_file:
    qid = int(query)
    qids.append(qid)
 
qrels = []
for line in data:
    qrels.append(line.split())
  
# Get the 'id' from the beginning of each line in the qrels file - this will
# be treated as the index for each query
indexes = []
for line in qrels:
    indexes.append(int(line[0])-1)
  
# Use the id's as the indexes and correct the ids to be the corresponding
# qid from the query file
correct_qids = []
for index in indexes:
    qid = qids[index]
    correct_qids.append(qid)
    
for i in range(len(qrels)):
    qrels[i][0] = str(correct_qids[i])
    
# Write the data with the corrected qids into a new file
f = open('corrected_qrels.text', 'w')
for i in range(len(qrels)):
    s = "%s %s %s %s\n" % (qrels[i][0], qrels[i][1], qrels[i][2], qrels[i][3])
    f.write(s)
f.close()