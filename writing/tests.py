
import spacy

def is_pattern_used(sentence, pattern):
    nlp = spacy.load("en_core_web_sm")
    sentence_doc = nlp(sentence.lower())
    pattern_doc = nlp(pattern.lower())
    new_sentence = ""
    new_sentence = " ".join([token.lemma_ if token.pos_ == "AUX" or token.pos_ == "VERB" else token.text for token in sentence_doc])
    new_pattern = " ".join([token.lemma_ if token.pos_ == "AUX" or token.pos_ == "VERB" else token.text for token in pattern_doc])
    if new_pattern in new_sentence:
        return True
    else:
        return False
    
print(is_pattern_used("I ate lunch yesterday.", "eat lunch"))