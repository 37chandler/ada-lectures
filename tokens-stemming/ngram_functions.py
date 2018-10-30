import random

def weighted_choice(freq_dist):
    weight_total = sum([count for token,count in freq_dist.items()])
    n = random.uniform(0, weight_total)
    for token, count in freq_dist.items() :
        if n < count:
            return(token)
        n = n - count
    return(token)
    
    
def generate_unigram(text,length=10) :
    fd = FreqDist(text)
    
    results = []
    for i in range(length) :
        results.append(weighted_choice(fd))
        
    return(" ".join(results))


def weighted_choice_ngram(cur_word,freq_dist) :
    ''' Starts with a current word and randomly chooses 
        a following word based on the bigrams. '''
    
    # First, build list of tuples of the form
    # ('a_word',count)
    # where our freq_dist has an entry like 
    # ('cur_word','a_word',count)
    sub_dist = {}
    
    for bigram, count in freq_dist.items() :
        if bigram[0] == cur_word :
            sub_dist[bigram[1]] = count
    
    return(weighted_choice(sub_dist))

def generate_bigram(text,length=10,start=None) :
    
    if not start :
        uni_fd = FreqDist(text)
        start = weighted_choice(uni_fd)
        
    fd = FreqDist(nltk.bigrams(text))
    
    results = []
    this_word = start
    for i in range(length) :
        this_word = weighted_choice_ngram(this_word,fd)
        results.append(this_word)
        
    return(" ".join(results))


