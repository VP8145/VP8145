
def find_extra_chars_with_positions(misspelled, candidate):
    from collections import Counter
    len_ms, len_cd = len(misspelled), len(candidate)

    if len_ms < len_cd:
        word1 = misspelled
        word2 = candidate
        operation = 'deleted'
    elif len_ms > len_cd:
        word2 = misspelled
        word1 = candidate
        operation = 'inserted'

    # Count the frequency of each character in word1
    count1 = Counter(word1)
    extra_chars_with_positions = []

    # Iterate over word2 to find extra characters and their positions
    for i, char in enumerate(word2):
        if count1[char] > 0:
            count1[char] -= 1
        else:
            extra_chars_with_positions.append((char, i,operation))

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
                    differences["transpositions"].append((i, word1[i], word1[i + 1], word2[i], word2[i + 1]))
                    i += 1  # Skip the next character since we detected a transposition
                else:
                    # Substitution
                    differences["substitutions"].append((i, char1, char2))
            i += 1 
    return differences
    

# Example usage
misspelled = "acress"
candidate = "acres"

if len(misspelled) == len(candidate):
     diffs=find_subst_transp(misspelled, candidate)
     print("\nSubstitutions (position, word1_char, word2_char):")
     for substitution in diffs["substitutions"]:
          print(substitution)

     print("\nTranspositions (position, word1_char1, word1_char2, word2_char1, word2_char2):")
     for transposition in diffs["transpositions"]:
          print(transposition)
else:
     extra_chars_with_positions = find_extra_chars_with_positions(misspelled, candidate)
     print("Extra characters in word2 that are not in word1 (character, position):")
     print(extra_chars_with_positions)





"""


def compare_words(word1, word2):
    len1, len2 = len(word1), len(word2)
    max_len = max(len1, len2)
    differences = {
        "insertions": [],
        "deletions": [],
        "substitutions": [],
        "transpositions": []
    }

    i = 0
    while i < max_len:
        char1 = word1[i] if i < len1 else None
        char2 = word2[i] if i < len2 else None
        
        
        if char1 != char2:
            if char1 is None:
                if len1 < len2:
                    # Insertion in word2
                    differences["insertions"].append((i, char2))
            elif char2 is None:
                if len1 > len2:
                    # Deletion in word2
                    differences["deletions"].append((i, char1))
            else:
                # Check for transpositions
                if (i + 1 < len1 and i + 1 < len2 and
                    word1[i] == word2[i + 1] and word1[i + 1] == word2[i]):
                    differences["transpositions"].append((i, word1[i], word1[i + 1], word2[i], word2[i + 1]))
                    i += 1  # Skip the next character since we detected a transposition
                else:
                    # Substitution
                    differences["substitutions"].append((i, char1, char2))
        i += 1

    return differences

# Example usage
word1 = "actress"
word2 = "acress"
diffs = compare_words(word1, word2)

print("Insertions (position, char):")
for insertion in diffs["insertions"]:
    print(insertion)

print("\nDeletions (position, char):")
for deletion in diffs["deletions"]:
    print(deletion)

print("\nSubstitutions (position, word1_char, word2_char):")
for substitution in diffs["substitutions"]:
    print(substitution)

print("\nTranspositions (position, word1_char1, word1_char2, word2_char1, word2_char2):")
for transposition in diffs["transpositions"]:
    print(transposition)




"""






"""

def compare_words(word1, word2):
    len1, len2 = len(word1), len(word2)
    max_len = max(len1, len2)
    differences = []

    for i in range(max_len):
        char1 = word1[i] if i < len1 else None
        char2 = word2[i] if i < len2 else None
        
        if char1 != char2:
            differences.append((i, char1, char2))

    return differences

# Example usage
word1 = "actress"
word2 = "acress"
diffs = compare_words(word1, word2)

print("Differences (position, word1, word2):")
for diff in diffs:
    print(diff)
"""    