
'''
   utility functions for processing terms

    shared by both indexing and query processing
'''
import string

from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
    
def isStopWord(word):
    ''' using the NLTK functions, return true/false'''    
    stop_words = set(stopwords.words('english'))
    
    # Keke provided a list of stop words but also requests we use the NLTK 
    # functions. Need to clarify what he would prefer us to use.
#    f = open('stopwords', 'r')
#    stop_words = f.read()
#    f.close()
    translation = word.maketrans('','',string.punctuation) # For edge cases where whole word is punctuation
    if word not in stop_words and word not in string.punctuation and word.translate(translation) != '':
        return False
    else:
        return True


def stemming(word):
    ''' return the stem, using a NLTK stemmer. check the project description 
    for installing and using it'''    
    stemmer = SnowballStemmer('english')
    return stemmer.stem(word)

def tokenize(doc):
    '''tokenizes the document'''
    tokens = word_tokenize((doc).lower())
    
    return tokens

def preprocess(doc):
    '''returns list of tokens that has been stemmed and stopwords have been 
    removed'''        
    # Tokenize the documents, then filter stop-words and stem tokens
    tokens = tokenize(doc)
    processed_tokens = []
        
    # Strip the '' off of each token so we can compare with stopword list
    for token in tokens:
        token = token[1:-1]
        
    for token in tokens:
        if isStopWord(token) is True:
            continue
        else:
            stemmed_token = stemming(token)
            processed_tokens.append(stemmed_token)
        
    return processed_tokens