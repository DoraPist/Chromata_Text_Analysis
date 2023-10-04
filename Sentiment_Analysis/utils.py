# utils
import spacy
import string

# from greek_stemmer import GreekStemmer

with open('stop_words.txt', encoding="utf8") as f:
    STOP_WORDS = f.readlines()

for i in range(len(STOP_WORDS)):
    STOP_WORDS[i] = STOP_WORDS[i].split('\n')[0]

eng = set("""a b c d e f g h i j k l m n o p q r s t u v w x y z""")

gre = set("""α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω ά έ ή ί ό ύ ώ""")

tone_dict = {'ά': 'α', 'έ': 'ε', 'ή': 'η', 'ί': 'ι', 'ό': 'ο', 'ύ': 'υ', 'ώ': 'ω'}

engw = 'abcdefghijklmnopqrstuvwxyz'
elw = 'αβψδεφγηιξκλμνοπ;ρστθωςχυζ'

word_dict = {'a': 'α', 'b': 'β', 'c': 'ψ', 'd': 'δ', 'e': 'ε', 'f': 'φ', 'g': 'γ', 'h': 'η', 'i': 'ι', 'j': 'ξ',
             'k': 'κ', 'l': 'λ', 'm': 'μ', 'n': 'ν', 'o': 'ο', 'p': 'π', 'q': ';', 'r': 'ρ', 's': 'σ', 't': 'τ',
             'u': 'θ', 'v': 'ω', 'w': 'ς', 'x': 'χ', 'y': 'υ', 'z': 'ζ'}
nlp = spacy.load("el_core_news_lg")


def clean_doc(doc, stop=False, unique=False, lemmatize=True, stem=False, rem_tones=False, pos_tag=False):
    doc = doc.lower()
    tokens = doc.split()
    tokens = correct_letter(tokens)

    tokens = remove_punct(tokens)

    # remove remaining tokens that are not alphabetic
    tokens = [word for word in tokens if word.isalpha()]

    if pos_tag:
        tokens = [token for token in tokens if
                  nlp(token)[0].pos_ == 'ADV' or nlp(token)[0].pos_ == 'NOUN' or nlp(token)[0].pos_ == 'ADJ' or
                  nlp(token)[0].pos_ == 'VERB' or nlp(token)[0].pos_ == 'SPACE']

    if lemmatize:
        tokens = [nlp(token)[0].lemma_.lower() for token in tokens]
        tokens = (' '.join(tokens)).split()

    if rem_tones:
        tokens = [remove_tones(word) for word in tokens]

    if stop:
        tokens = remove_stop(tokens, 0)

    if stem:
        tokens = [token.upper() for token in tokens]
        tokens = stem_words(tokens)
        # doc=rem_stop(tokens,stem)

    if unique:
        tokens = unique_words(tokens)

    # filter out short tokens
    tokens = [word for word in tokens if len(word) > 1]

    return tokens


def clean_df(df, stop=False, unique=False, lemmatize=True, stem=False, rem_tones=False):
    col_names = list(df.columns)
    index = col_names.index('text')
    # load the doc
    if stem:

        stemmer = GreekStemmer()

    for i in range(len(df)):
        tokens = clean_doc(df.iloc[i, index], stop, unique, lemmatize, stem, rem_tones)
        # filter by vocab
        # tokens = [w for w in tokens if w in vocab]

        df.iloc[i, index] = ' '.join(tokens)
    return df.copy()


def remove_punct(tokens):
    # remove punctuation from each token
    string_punctuation = string.punctuation + '’0123456789«»'
    # string_punctuation = '!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~' + '’0123456789«»'
    temp_tokens = []
    for token in tokens:
        temp_tokens.extend(token.split('-'))

    table = str.maketrans('', '', string_punctuation)
    tokens = [w.translate(table) for w in temp_tokens]
    return tokens


def remove_stop(tokens, stem):
    if stem:
        # tokens = [w for w in tokens if not w in STOP_WORDS_STEM]
        tokens = [w for w in tokens if not (w in STOP_WORDS or remove_tones(w) in STOP_WORDS_STEM)]
    else:
        # tokens = [w for w in tokens if not w in STOP_WORDS]
        tokens = [w for w in tokens if not (w in STOP_WORDS or remove_tones(w) in STOP_WORDS)]

    return tokens


def remove_tones(word):
    new_word = []
    for letter in word:
        if letter in tone_dict:
            new_word.append(tone_dict[letter])
        else:
            new_word.append(letter)

    return ''.join(new_word)


def stem_words(tokens):
    from greek_stemmer import GreekStemmer
    stemmer = GreekStemmer()
    tokens = [stemmer.stem(token) for token in tokens]
    return tokens


def unique_words(tokens):
    unique_words = []
    seen = set()
    j = 0
    for i in tokens:
        if i not in seen:
            unique_words.append(i)
        seen.add(i)
    # return ' '.join(unique_words)
    return unique_words


def correct_letter(tokens):
    newtokens = []
    for token in tokens:
        engcount = 0
        grecount = 0
        count = 0
        poseng = []
        posgre = []
        temptoken = []
        for letter in token:
            temptoken.append(letter)
            count += 1
            if letter in eng:
                poseng.append(count)
                engcount += 1
            elif letter in gre:
                posgre.append(count)
                grecount += 1
        if grecount >= engcount:
            if engcount > 0:
                for pos in poseng:
                    temptoken[pos - 1] = word_dict[temptoken[pos - 1]]
        newtoken = ''.join(temptoken)
        newtokens.append(newtoken)
    return newtokens.copy()


