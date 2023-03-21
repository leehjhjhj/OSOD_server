
import spacy

def is_pattern_used(sentence, pattern):
    sentence = sentence.replace("'ve", " have").replace("'ll", " will").replace("n't", " not").replace("re", " are")
    pattern = pattern.replace("'ve", " have").replace("'ll", " will").replace("n't", " not").replace("re", " are")

    nlp = spacy.load("en_core_web_sm")
    pattern_doc = nlp(pattern.lower())
    for doc in pattern_doc:
        if doc.lemma_ == "will":
            sentence = sentence.replace("'d", " would")
        elif doc.lemma_ == "have":
            sentence = sentence.replace("'d", " had").replace("'s", " has")

    sentence_doc = nlp(sentence.lower())

    new_sentence = " ".join([token.lemma_ if token.pos_ == "AUX" or token.pos_ == "VERB" else token.text for token in sentence_doc])
    new_pattern = " ".join([token.lemma_ if token.pos_ == "AUX" or token.pos_ == "VERB" else token.text for token in pattern_doc])

    if new_pattern in new_sentence:
        return True
    else:
        return False
    
print(is_pattern_used("She's good at him", "has good at"))
