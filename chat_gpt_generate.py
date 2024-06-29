import nltk
from nltk.tokenize import RegexpTokenizer
import re
from collections import Counter
import itertools
from spellchecker import SpellChecker


spell = SpellChecker()
count1_edit = {}
corp_words_freq={}

def tokenizeData(data):
    print("Tokenizing data...")
    tokenizer = RegexpTokenizer(r'\w+') # remove punctuation
    corpus=tokenizer.tokenize(data.lower())  # convert to lowercase and tokenize
    
    return corpus

# Counter stores the frequency of each word in the corpus (big.txt).
# words function is used to tokenize the content of 'big.txt', and the Counter is created to count the occurrences of each word.
def words(text):
    #return re.findall(r'\w+', text.lower())
    corpus = tokenizeData(text)
    
    return corpus

corpus = words(open(r"C:\Users\Public\big.txt").read())
corp_words_freq = Counter(corpus)


def compare_build_cnt(misspelled, candidates):
    

    def add_or_increment(count1_edit, key):
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
                    key = word2[i - 1] + "|" + word2[i - 1] + char
                    #print("key = ", key)
                    add_or_increment(count1_edit, key)
                elif operation == 'inserted':
                    key = char + "|" + " "
                    add_or_increment(count1_edit, key)

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
                    add_or_increment(count1_edit, key)
                    i += 1  # Skip the next character since we detected a transposition
                else:
                    # Substitution
                    operation = 'substitution'
                    differences["substitutions"].append((i, char1, char2))
                    key = char1 + "|" + char2
                    add_or_increment(count1_edit, key)

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


# iterating through tokens in corpus
for word in itertools.islice(corp_words_freq, 100):
    print(f"Given word: {word}")

    misspelled = spell.unknown([word])
    if misspelled:
        candidates = spell.candidates(word)
        print(candidates)
        compare_build_cnt(word, candidates)
    else:
        print(f"Valid: {word}")


print(count1_edit)
