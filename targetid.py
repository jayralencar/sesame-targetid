from nltk import word_tokenize, pos_tag, WordNetLemmatizer
from nltk.corpus import wordnet as wn
from nltk.corpus import framenet as fn
from optparse import OptionParser

optpr = OptionParser()
optpr.add_option("--raw_input", type="str", metavar="FILE")
(options, args) = optpr.parse_args()

lemmatizer =  WordNetLemmatizer()

def pos_map(pos):
    poss = {
        'NN':wn.NOUN, 'JJ':wn.ADJ,
        'VB':wn.VERB, 'RB':wn.ADV
    }
    try:
        return poss[pos[:2]]
    except:
        return None
    
def get_fn_pos(pos):
    poss = {
        'NN':'n',
        'VB':'v',
        'JJ':'a',
        'RB':'adv',
        'IN':'prep',
    }

    try:
        return poss[pos[:2]]
    except:
        return None

def get_fn_pos_by_rules(pos, token):
    """
    Rules for mapping NLTK part of speech tags into FrameNet tags, based on co-occurrence
    statistics, since there is not a one-to-one mapping.
    """
    if pos[0] == "v" or pos in ["rp", "ex", "md"]:  # Verbs
        rule_pos = "v"
    elif pos[0] == "n" or pos in ["$", ":", "sym", "uh", "wp"]:  # Nouns
        rule_pos = "n"
    elif pos[0] == "j" or pos in ["ls", "pdt", "rbr", "rbs", "prp"]:  # Adjectives
        rule_pos = "a"
    elif pos == "cc":  # Conjunctions
        rule_pos = "c"
    elif pos in ["to", "in"]:  # Prepositions
        rule_pos = "prep"
    elif pos in ["dt", "wdt"]:  # Determinors
        rule_pos = "art"
    elif pos in ["rb", "wrb"]:  # Adverbs
        rule_pos = "adv"
    elif pos == "cd":  # Cardinal Numbers
        rule_pos = "num"
    else:
        # sys.stderr.write("WARNING: Rule not defined for part-of-speech {} word {} - treating as noun.".format(pos, token))
        return "n"
    return rule_pos

def lemmatize(tokens):
    res = []
    for word, pos in tokens:
        tag = pos_map(pos)
        if tag == None:
            res.append([word, pos, lemmatizer.lemmatize(word)])
            # print(lemmatizer.lemmatize(word))
        else:
            res.append([word, pos, lemmatizer.lemmatize(word, tag)])
    return res

file = open(options.raw_input)

savetext = ''

for line in file.readlines():
    
    text = line

    tokens = word_tokenize(text)

    tagged = pos_tag(tokens)


    targeted = []
    targets = []
    for word, pos, lemma in lemmatize(tagged):
        fn_pos = get_fn_pos(pos)
        target = '_'
        if fn_pos != None:
            # print(word+'.'+fn_pos)
            lus = fn.lu_ids_and_names(lemma+'.'+fn_pos)
            # print(lus)
            for _id in lus:
                if lus[_id] == lemma+'.'+fn_pos:
                    target = lemma+'.'+fn_pos
                    targets.append(target)
                    break
        targeted.append([word, pos, lemma, target])

    # print(targets)
    # print(targeted)
    sentence_id = 1
    for target in targets:
        sentence = ''
        i = 1
        for word,pos,lemma, tg in targeted:
            _tg = '_'
            if tg == target:
                _tg = tg
            line = str(i)+"\t"+word+"\t_\t"+lemma+"\t"+pos.lower()+"\t"+pos+"\t"+str(sentence_id)+"\t_\t_\t_\t_\t_\t"+_tg+"\t_\t0\n"
            sentence = sentence+line   
            i = i +1
        savetext = savetext+sentence+'\n'
        sentence_id = sentence_id + 1

    
with open('output.conll','w') as file:
        file.write(savetext)