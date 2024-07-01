import nltk
from nltk.tokenize import RegexpTokenizer
import re
from collections import Counter
import itertools
from spellchecker import SpellChecker


spell = SpellChecker()
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

    def find_extra_chars_with_positions(misspelled, candidate):
        len_ms, len_cd = len(misspelled), len(candidate)

        if len_ms < len_cd:
            word1 = misspelled
            word2 = candidate
            operation = 'deleted'
        elif len_ms > len_cd:
            word2 = misspelled
            word1 = candidate
            operation = 'inserted'
        else:
            return []

        # Count the frequency of each character in word1
        count1 = Counter(word1)
        extra_chars_with_positions = []

        # Iterate over word2 to find extra characters and their positions
        for i, char in enumerate(word2):
            if count1[char] > 0:
                count1[char] -= 1
            else:
                extra_chars_with_positions.append((char, i, operation))
                # adding to count_edit dictionary
                if operation == 'deleted':
                    if i==0:  # If the character deleted is the begining character of that word
                        key = word2[i + 1]  + "|" + char + word2[i + 1] 
                    else:
                        key = word2[i - 1] + "|" + word2[i - 1] + char 
                    #print("key = ", key)
                    add_or_increment(candidate,count1_edit, key)
                elif operation == 'inserted':
                    key = char + "|" + " "
                    add_or_increment(candidate,count1_edit, key)

        return extra_chars_with_positions

    def find_subst_transp(misspelled, candidate):
        differences = {
            "substitutions": [],
            "transpositions": []
        }

        len_ms, len_cd = len(misspelled), len(candidate)
        word1 = misspelled
        word2 = candidate
        i = 0
        while i < len_ms:
            char1 = word1[i] if i < len_ms else None
            char2 = word2[i] if i < len_cd else None

            if char1 != char2:
                # Check for transpositions
                if (i + 1 < len_ms and i + 1 < len_cd and
                        word1[i] == word2[i + 1] and word1[i + 1] == word2[i]):
                    operation = 'transposition'
                    differences["transpositions"].append((i, word1[i], word1[i + 1], word2[i], word2[i + 1]))
                    key = word1[i] + word1[i + 1] + '|' + word2[i] + word2[i + 1]
                    add_or_increment(candidate,count1_edit, key)
                    i += 1  # Skip the next character since we detected a transposition
                else:
                    # Substitution
                    operation = 'substitution'
                    differences["substitutions"].append((i, char1, char2))
                    key = char1 + "|" + char2
                    add_or_increment(candidate,count1_edit, key)

            i += 1
        return differences

    if candidates:
        for candidate in candidates:
            if len(misspelled) == len(candidate):
                diffs = find_subst_transp(misspelled, candidate)
                #for substitution in diffs["substitutions"]:
                #    print(substitution)
                #for transposition in diffs["transpositions"]:
                #    print(transposition)
            else:
                extra_chars_with_positions = find_extra_chars_with_positions(misspelled, candidate)
                #print(extra_chars_with_positions)

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


## Main program starts here
# iterating through tokens in corpus
corpus = words(open(r"C:\Users\Public\big.txt").read())
#print('total_spaces - post words ',total_spaces)
corp_words_freq = Counter(corpus)

for word in itertools.islice(corp_words_freq, 100):
    #print(f"Given word: {word}")

    misspelled = spell.unknown([word])
    if misspelled:
        candidates = spell.candidates(word)
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
     for c in cd:
            #print(ms,c) 
            e_given_char = candidate_and_edit1[c] #c|ct
            #print(ms,c,e_given_char) 
            cnt_e_given_char = count1_edit[e_given_char] # count(ct)
            #print(ms,c,e_given_char,cnt_e_given_char) 
            prob_candidate_in_corpus = corpusProb[c] # P(W)
            #print(ms,c,e_given_char,cnt_e_given_char,prob_candidate_in_corpus)
            suffix = e_given_char.split('|')[1]
            cnt_denominator = substring_counts[suffix]
            #print(ms, c, e_given_char, cnt_e_given_char, prob_candidate_in_corpus, cnt_denominator)
            prob_error_model = (cnt_e_given_char/cnt_denominator )*prob_candidate_in_corpus # P(e/w)*p(w)
            print(ms, c, e_given_char, cnt_e_given_char, prob_candidate_in_corpus, prob_error_model)

  
#calculating trigram prob
#getTrigramProb()



