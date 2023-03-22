

 
import spacy

# Load the model only once
nlp = spacy.load("en_core_web_sm")

# Create a dictionary for pattern replacement
patterns = {"'ve": " have", "'ll": " will", "n't": " not", "'re": " are"}

def is_pattern_used(sentence, pattern):
    for old, new in patterns.items():
        sentence = sentence.replace(old, new)
        pattern = pattern.replace(old, new)

    pattern_doc = nlp(pattern.lower())
    for doc in pattern_doc:
        if doc.lemma_ == "will":
            sentence = sentence.replace("'d", " would")
        elif doc.lemma_ == "have":
            sentence = sentence.replace("'d", " had").replace("'s", " has")

    sentence_doc = nlp(sentence.lower())

    # Use a generator expression instead of a list comprehension
    new_sentence = " ".join(token.lemma_ if token.pos_ in {"AUX", "VERB"} else token.text for token in sentence_doc)
    new_pattern = " ".join(token.lemma_ if token.pos_ in {"AUX", "VERB"} else token.text for token in pattern_doc)

    return new_pattern in new_sentence

print(is_pattern_used("He'd good at him", "have good at"))


