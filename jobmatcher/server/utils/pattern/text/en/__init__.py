#### PATTERN | EN ########################################################
# -*- coding: utf-8 -*-
# Copyright (c) 2010 University of Antwerp, Belgium
# Author: Tom De Smedt <tom@organisms.be>
# License: BSD (see LICENSE.txt for details).
# http://www.clips.ua.ac.be/pages/pattern

##########################################################################
# English linguistical tools using fast regular expressions.

import os
import sys

try:
    MODULE = os.path.dirname(os.path.realpath(__file__))
except:
    MODULE = ""

sys.path.insert(0, os.path.join(MODULE, "..", "..", "..", ".."))

# Import parser base classes.


from jobmatcher.server.utils.pattern.text import Lexicon
from jobmatcher.server.utils.pattern.text import Model
from jobmatcher.server.utils.pattern.text import Morphology
from jobmatcher.server.utils.pattern.text import Context
from jobmatcher.server.utils.pattern.text import Parser as _Parser
from jobmatcher.server.utils.pattern.text import ngrams
from jobmatcher.server.utils.pattern.text import pprint
from jobmatcher.server.utils.pattern.text import commandline
from jobmatcher.server.utils.pattern.text import PUNCTUATION



# Import parser universal tagset.


from jobmatcher.server.utils.pattern.text import penntreebank2universal
from jobmatcher.server.utils.pattern.text import PTB
from jobmatcher.server.utils.pattern.text import PENN
from jobmatcher.server.utils.pattern.text import UNIVERSAL
from jobmatcher.server.utils.pattern.text import NOUN
from jobmatcher.server.utils.pattern.text import VERB
from jobmatcher.server.utils.pattern.text import ADJ
from jobmatcher.server.utils.pattern.text import ADV
from jobmatcher.server.utils.pattern.text import PRON
from jobmatcher.server.utils.pattern.text import DET
from jobmatcher.server.utils.pattern.text import PREP
from jobmatcher.server.utils.pattern.text import ADP
from jobmatcher.server.utils.pattern.text import NUM
from jobmatcher.server.utils.pattern.text import CONJ
from jobmatcher.server.utils.pattern.text import INTJ
from jobmatcher.server.utils.pattern.text import PRT
from jobmatcher.server.utils.pattern.text import PUNC
from jobmatcher.server.utils.pattern.text import X



# Import parse tree base classes.

from jobmatcher.server.utils.pattern.text.tree import Tree
from jobmatcher.server.utils.pattern.text.tree import Text
from jobmatcher.server.utils.pattern.text.tree import Sentence
from jobmatcher.server.utils.pattern.text.tree import Slice
from jobmatcher.server.utils.pattern.text.tree import Chunk
from jobmatcher.server.utils.pattern.text.tree import PNPChunk
from jobmatcher.server.utils.pattern.text.tree import Chink
from jobmatcher.server.utils.pattern.text.tree import Word
from jobmatcher.server.utils.pattern.text.tree import table
from jobmatcher.server.utils.pattern.text.tree import SLASH
from jobmatcher.server.utils.pattern.text.tree import WORD
from jobmatcher.server.utils.pattern.text.tree import POS
from jobmatcher.server.utils.pattern.text.tree import CHUNK
from jobmatcher.server.utils.pattern.text.tree import PNP
from jobmatcher.server.utils.pattern.text.tree import REL
from jobmatcher.server.utils.pattern.text.tree import ANCHOR
from jobmatcher.server.utils.pattern.text.tree import LEMMA
from jobmatcher.server.utils.pattern.text.tree import AND
from jobmatcher.server.utils.pattern.text.tree import OR




# Import sentiment analysis base classes.

from jobmatcher.server.utils.pattern.text import (
    Sentiment as _Sentiment, NOUN, VERB, ADJECTIVE, ADVERB
)


# Import spelling base class.
from jobmatcher.server.utils.pattern.text import (
    Spelling
)




# Import verb tenses.
from jobmatcher.server.utils.pattern.text import (
    INFINITIVE, PRESENT, PAST, FUTURE,
    FIRST, SECOND, THIRD,
    SINGULAR, PLURAL, SG, PL,
    PROGRESSIVE,
    PARTICIPLE
)



# Import inflection functions.

from jobmatcher.server.utils.pattern.text.en.inflect import (
    article, referenced, DEFINITE, INDEFINITE,
    pluralize, singularize, NOUN, VERB, ADJECTIVE,
    grade, comparative, superlative, COMPARATIVE, SUPERLATIVE,
    verbs, conjugate, lemma, lexeme, tenses,
    predicative, attributive

)



# Import quantification functions.
from jobmatcher.server.utils.pattern.text.en.inflect_quantify import (
    number, numerals, quantify, reflect
)



# Import mood & modality functions.
from jobmatcher.server.utils.pattern.text.en.modality import (
    mood, INDICATIVE, IMPERATIVE, CONDITIONAL, SUBJUNCTIVE,
    modality, uncertain, EPISTEMIC,
    negated
)

from jobmatcher.server.utils.pattern.text.en import (
    inflect, wordnet, wordlist
)


sys.path.pop(0)

#--- ENGLISH PARSER ------------------------------------------------------


def find_lemmata(tokens):
    """ Annotates the tokens with lemmata for plural nouns and conjugated verbs,
        where each token is a [word, part-of-speech] list.
    """
    for token in tokens:
        word, pos, lemma = token[0], token[1], token[0]
        # cats => cat
        if pos == "NNS":
            lemma = singularize(word)
        # sat => sit
        if pos.startswith(("VB", "MD")):
            lemma = conjugate(word, INFINITIVE) or word
        token.append(lemma.lower())
    return tokens


class Parser(_Parser):

    def find_lemmata(self, tokens, **kwargs):
        return find_lemmata(tokens)

    def find_tags(self, tokens, **kwargs):
        if kwargs.get("tagset") in (PENN, None):
            kwargs.setdefault("map", lambda token, tag: (token, tag))
        if kwargs.get("tagset") == UNIVERSAL:
            kwargs.setdefault(
                "map", lambda token, tag: penntreebank2universal(token, tag))
        return _Parser.find_tags(self, tokens, **kwargs)


class Sentiment(_Sentiment):

    def load(self, path=None):
        _Sentiment.load(self, path)
        # Map "terrible" to adverb "terribly" (+1% accuracy)
        if not path:
            for w, pos in list(dict.items(self)):
                if "JJ" in pos:
                    if w.endswith("y"):
                        w = w[:-1] + "i"
                    if w.endswith("le"):
                        w = w[:-2]
                    p, s, i = pos["JJ"]
                    self.annotate(w + "ly", "RB", p, s, i)

parser = Parser(
    # A dict of known words => most frequent tag.
    lexicon=os.path.join(MODULE, "en-lexicon.txt"),
    # A dict of word frequency.
    frequency=os.path.join(MODULE, "en-frequency.txt"),
    # A SLP classifier trained on WSJ (01-07).
    model=os.path.join(MODULE, "en-model.slp"),
    # A set of suffix rules (e.g., -ly = adverb).
    morphology=os.path.join(MODULE, "en-morphology.txt"),
    # A set of contextual rules.
    context=os.path.join(MODULE, "en-context.txt"),
    # A dict of named entities: John = NNP-PERS.
    entities=os.path.join(MODULE, "en-entities.txt"),
    default=("NN", "NNP", "CD"),
    language = "en"
)

lexicon = parser.lexicon  # Expose lexicon.

sentiment = Sentiment(
    path=os.path.join(MODULE, "en-sentiment.xml"),
    synset="wordnet_id",
    negations=("no", "not", "n't", "never"),
    modifiers = ("RB",),
    modifier = lambda w: w.endswith("ly"),
    tokenizer = parser.find_tokens,
    language = "en"
)

spelling = Spelling(
    path=os.path.join(MODULE, "en-spelling.txt")
)


def tokenize(s, *args, **kwargs):
    """Returns a list of sentences, where punctuation marks have been split
    from words."""
    return parser.find_tokens(s, *args, **kwargs)


def parse(s, *args, **kwargs):
    """Returns a tagged Unicode string."""
    return parser.parse(s, *args, **kwargs)


def parsetree(s, *args, **kwargs):
    """Returns a parsed Text from the given string."""
    return Text(parse(s, *args, **kwargs))


def tree(s, token=[WORD, POS, CHUNK, PNP, REL, LEMMA]):
    """Returns a parsed Text from the given parsed string."""
    return Text(s, token)


def tag(s, tokenize=True, encoding="utf-8", **kwargs):
    """ Returns a list of (token, tag)-tuples from the given string.
    """
    tags = []
    for sentence in parse(s, tokenize, True, False, False, False, encoding, **kwargs).split():
        for token in sentence:
            tags.append((token[0], token[1]))
    return tags


def keywords(s, top=10, **kwargs):
    """Returns a sorted list of keywords in the given string."""
    return parser.find_keywords(s, **dict({
        "frequency": parser.frequency,
        "top": top,
        "pos": ("NN",),
        "ignore": ("rt",)}, **kwargs))


def suggest(w):
    """ Returns a list of (word, confidence)-tuples of spelling corrections.
    """
    return spelling.suggest(w)


def polarity(s, **kwargs):
    """ Returns the sentence polarity (positive/negative) between -1.0 and 1.0.
    """
    return sentiment(s, **kwargs)[0]


def subjectivity(s, **kwargs):
    """ Returns the sentence subjectivity (objective/subjective) between 0.0 and 1.0.
    """
    return sentiment(s, **kwargs)[1]


def positive(s, threshold=0.1, **kwargs):
    """ Returns True if the given sentence has a positive sentiment (polarity >= threshold).
    """
    return polarity(s, **kwargs) >= threshold

split = tree  # Backwards compatibility.

#-------------------------------------------------------------------------
# python -m pattern.en xml -s "The cat sat on the mat." -OTCL

if __name__ == "__main__":
    commandline(parse)