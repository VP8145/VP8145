import nltk
from nltk.tokenize import RegexpTokenizer
import re
from collections import Counter
import itertools
from spellchecker import SpellChecker

candidate_prob={}
final_error_suggestion={}
errors = []
spell = SpellChecker(language='en') # english language dictionary
count1_edit = {}
corp_words_freq={}
candidate_and_edit1= {} # misspelled words and their respective edits
corpusProb={} # probablities of candidates 
error_and_candidates={} # to hold {mispelled word : candidate1, candidate2,...}

def tokenizeData(data):
    print("Tokenizing data...")
    tokenizer = RegexpTokenizer(r'\w+') # remove punctuation
    corpus=tokenizer.tokenize(data.lower())  # convert to lowercase and tokenize
    
    return corpus

def getWordProb(corp_words_freq, corpusSize, candidates):
    for word in candidates:
        prob = corp_words_freq[word] / corpusSize
        #print(f"P({word}) = {prob}")
        corpusProb[word] = prob
    return corpusProb



# Counter stores the frequency of each word in the corpus (big.txt).
# words function is used to tokenize the content of 'big.txt', and the Counter is created to count the occurrences of each word.
def words(text):
    global total_spaces
    # Regular expression to find sequences of spaces followed by a word
    pattern = re.compile(r'(\s+)\w')
    matches = pattern.findall(text)
    # Calculate the total number of spaces
    total_spaces = sum(len(match) for match in matches)
    corpus = tokenizeData(text)
    
    return corpus



def createErrorCandidatesDict(word,candidates):
    if candidates:
        if error_and_candidates.get(word) is None:
            error_and_candidates[word] = candidates
            #print('error_and_candidates : ', error_and_candidates)


def compare_build_cnt(misspelled, candidates):
    

    def add_or_increment(candidate,count1_edit, key):
        candidate_and_edit1[candidate] = key # populating 
        if key in count1_edit:
            count1_edit[key] += 1
        else:
            count1_edit[key] = 1

    def error_combinations(error, candidate):
        if len(candidate) > len(error):
            for idx in range(len(candidate)):
                #print(f' {candidate[:idx]} + {candidate[idx + 1:] }') 
                if candidate[:idx] + candidate[idx + 1:] == error:
                    if candidate[:idx] != '': # to check if its SOS
                        errors.append(('deleted', candidate[idx-1],candidate[idx-1] + candidate[idx]))
                        key=candidate[idx-1] + '|' + candidate[idx-1] + candidate[idx]
                    else:
                        errors.append(('deleted', candidate[idx+1],candidate[idx]+candidate[idx+1]))
                        key=candidate[idx+1] + '|' + candidate[idx] + candidate[idx+1] 
                                      
                    add_or_increment(candidate,count1_edit, key)

        elif len(candidate) < len(error):
            for idx in range(len(candidate) + 1):
                prefix = candidate
                suffix = ""
                if idx < len(candidate):
                    prefix = candidate[:idx]
                    suffix = candidate[idx:]
                #print(f' {prefix} + {error[idx]} +{suffix}') 
                if prefix + error[idx] + suffix == error:
                    if len(prefix) > 0:
                        errors.append(('inserted', prefix[-1] + error[idx], prefix[-1]))
                        key=prefix[-1] + error[idx] + '|' + prefix[-1] 
                    else:
                        errors.append(('inserted', error[idx], ""))
                        key=error[idx] + '|' + ' '  # considering space instead  of empty string
                    add_or_increment(candidate,count1_edit, key)    
        else:
            for idx in range(len(candidate)):
                if idx < len(candidate) - 1 and \
                    candidate[idx + 1] != candidate[idx] and \
                    candidate[idx + 1] + candidate[idx] == error[idx] + error[idx + 1]:
                        errors.append(('transposition', candidate[idx + 1] + candidate[idx], candidate[idx] + candidate[idx + 1]))
                        key= candidate[idx + 1] + candidate[idx] + '|' + candidate[idx] + candidate[idx + 1]
                        add_or_increment(candidate,count1_edit, key)    
                elif candidate[idx] != error[idx] and candidate[:idx] == error[:idx] and candidate[idx + 1:] == error[idx + 1:]:
                    errors.append(('substitution', error[idx],candidate[idx]))
                    key=error[idx] + '|' + candidate[idx]
                    add_or_increment(candidate,count1_edit, key)    
                    
       
    
    if candidates:
       for candidate in candidates:
           error_combinations(misspelled, candidate)
    

#####################################################
#####################################################
def getConditionalCount(count1_edit):
    substring_counts = Counter()
    x_keys = list(count1_edit.keys())
    #print('x_keys =',x_keys)
    suffixes_to_count = [item.split('|')[1] for item in x_keys]
    suffixes_to_count = set(suffixes_to_count)
    #print(suffixes_to_count)
    for substring in suffixes_to_count:
        if substring == ' ':
            substring_counts[substring] = total_spaces
        else:
            substring_counts[substring] = corpus.count(substring)

    #print('substring_counts')
    #print(substring_counts)
    return substring_counts

# final suggestion og word based on corpus for the misspelled word
def write_max_prob_candidate(ms,candidate_prob):
    Keymax = max(zip(candidate_prob.values(), candidate_prob.keys()))[1]
    final_error_suggestion[ms]= Keymax


## Main program starts here
# iterating through tokens in corpus
corpus = words(open(r"C:\Users\Public\big.txt").read())
#print('total_spaces - post words ',total_spaces)
corp_words_freq = Counter(corpus)

for word in itertools.islice(corp_words_freq, 1000):
    #print(f"Given word: {word}")
    misspelled = spell.unknown([word])
    if misspelled:
        candidates = spell.candidates(word) # use this to get all possible candidates
        #candidates = spell.edit_distance_1(word) # use this to get candidates which are only at 1 edit distance
        #print(f"candidates for given word: {candidates}")
        createErrorCandidatesDict(word,candidates)
        compare_build_cnt(word, candidates)
        if candidates:
            #calculating P(W) for candidates
            corpusProb=getWordProb(corp_words_freq, len(corpus), candidates)
            
    #else:
        #print(f"Valid: {word}")

#calculating P(-/W) from corpus
substring_counts=getConditionalCount(count1_edit)

#print(count1_edit) #{'k|kr': 1, 'e| ': 4, 'r| ': 3, 's|c': 1, 'e|a': 1, 's| ': 1, 'l| ': 1, 'm| ': 1, 'r|n': 1, 'u|e': 5, ...}
#print(substring_counts) # Counter({'a': 21124, 'he': 12401, 'i': 7684, 'o': 257, 'c': 128, 'e': 115, 'f': 111, 'l': 67, 'n': 61, 'u': 24, 'ra': 1, 'nm': 1, 'rf': 0, ' ': 0, 'kr': 0})
#print(error_and_candidates) #{'ebook': {'rebook', 'book'}, 'sherlock': {'shlock', 'shylock', 'hemlock', 'charlock'}, ...}
#print(corp_words_freq) #  ({'filth': 1, 'lamentations': 1, 'moslem': 1, 'glen': 1, 'buggy': 1, 'folio': 1, 'syrian': 1, 'wench': 1, 'wiki': 1, 'frequency_lists': 1, 'xrange': 1, 'min': 1})
#print(corpusProb) # {'rebook': 0.0, 'book': 9.591380307193087e-05, 'hemlock': 0.0, 'shlock': 0.0, 'shylock': 0.0, 'charlock': 0.0, 'homes': 3.137367390203346e-05, 'holes': 6.2747347804066925e-06, 'aether': 0.0}
#print(candidate_and_edit1) #{'book': 'e| ', 'rebook': 'k|kr', 'shylock': 'r| ', 'hemlock': 'r| ', 'shlock': 'r| ', 'charlock': 'e|a'}


#def calculateNosiyChannelProb():
for  ms,cd in error_and_candidates.items(): 
     candidate_prob.clear()
     found_probable_candidate =False
     for c in cd:
            #print(ms,c)
            if  c in candidate_and_edit1: # check if there is any candidate at edit distance 1
                e_given_char = candidate_and_edit1[c] #c|ct
                #print(ms,c,e_given_char) 
                cnt_e_given_char = count1_edit[e_given_char] # count(ct)
                #print(ms,c,e_given_char,cnt_e_given_char) 
                prob_candidate_in_corpus = corpusProb[c] # P(W)
                #print(ms,c,e_given_char,cnt_e_given_char,prob_candidate_in_corpus)
                suffix = e_given_char.split('|')[1]
                cnt_denominator = substring_counts[suffix]
                if cnt_denominator > 0 :
                    prob_error_model = (cnt_e_given_char/cnt_denominator )*prob_candidate_in_corpus # P(e/w)*p(w)
                    #print('final error model',ms, c, e_given_char, cnt_e_given_char, prob_candidate_in_corpus, prob_error_model)
                    #print(f'(ms) {ms}, (c) {c}, (mistake is) {e_given_char},  (count of mistakes) {cnt_e_given_char}, (p({c})) {prob_candidate_in_corpus},  (P(e/w)*p(w)) {prob_error_model}')
                    if prob_error_model > 0 : # only if the candidate probablity is > 0 we will add it to the final suggestion list
                        found_probable_candidate = True
                        candidate_prob[c]=prob_error_model # collecting {candidate : probablity}
                else:
                    one=1
                    #print(f'Probablity of {c} is 0 ')

                
            else:
                one=1
                #print(f'{c} is not at 1 edit dist from {ms}')
     if found_probable_candidate: # we will populate final suggettion list only for misspeled words which have  probablity > 0 based on our corpus
         write_max_prob_candidate(ms,candidate_prob)        



print('==== final ====')
print(final_error_suggestion)


