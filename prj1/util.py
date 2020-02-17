
'''
   utility functions for processing terms

    shared by both indexing and query processing
'''

def isStopWord(word):
    ''' using the NLTK functions, return true/false'''
    
    f = open('stopwords', 'r')
    stop_words = f.readlines()
    f.close()
    
    if word not in stop_words:
        return False
    else:
        return True


def stemming(word):
    ''' return the stem, using a NLTK stemmer. check the project description 
    for installing and using it'''
    
    from nltk.stem import SnowballStemmer
    
    stemmer = SnowballStemmer('english')
    return stemmer.stem(word)
