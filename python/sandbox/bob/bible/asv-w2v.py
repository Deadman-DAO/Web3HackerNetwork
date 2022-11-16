import bz2
import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import re

import w3hn.hadoop.parquet_util as pq_util
from w3hn.aws.aws_util import S3Util
from w3hn.data.bible import asv_constants
from w3hn.log.log_init import logger
log = logger(__file__)

profile = 'w3hn-admin'
bucket = 'deadmandao'
asv_path = 'web3hackernetwork/data_pipeline/raw/bible_asv'

s3_util = S3Util(bucket_name = bucket, profile = profile)
table = s3_util.read_parquet_table(asv_path)

asv = table.to_pandas()

con = duckdb.connect()
texts = con.query('select category, subcategory, book, text from asv').to_df()
word_set = set()
word_counts = dict()
word_list = list()
book_words_map = dict()
subcategory_words_map = dict()
category_words_map = dict()
books = asv_constants.OT + asv_constants.NT
subcategories = asv_constants.SUBCATEGORIES
categories = asv_constants.CATEGORIES
for book in books: book_words_map[book] = list()
for subcategory in subcategories: subcategory_words_map[subcategory] = list()
for category in categories: category_words_map[category] = list()
for row in texts.itertuples():#['text', 'book']:
    category = row[1]
    subcategory = row[2]
    book = row[3]
    text = row[4]
    book_words = book_words_map[book]
    subcategory_words = subcategory_words_map[subcategory]
    category_words = category_words_map[category]
    for word in text.split(' '):
        word = re.search('([a-zA-Z\-]*)', word).group(1)
        if word and word != '':
            word_set.add(word)
            word_list.append(word)
            book_words.append(word)
            subcategory_words.append(word)
            category_words.append(word)
            if word not in word_counts:
                word_counts[word] = 0
            word_counts[word] += 1

print(f'{len(word_set)} unique words')

book_words_array = list()
for book in books:
    book_words_array.append(' '.join(book_words_map[book]))
subcategory_words_array = list()
for subcategory in subcategories:
    subcategory_words_array.append(' '.join(subcategory_words_map[subcategory]))
category_words_array = list()
for category in categories:
    category_words_array.append(' '.join(category_words_map[category]))
# book_words_array = \
#     [' '.join(words) for words in book_words_map.values()]
# subcategory_words_array = \
#     [' '.join(words) for words in subcategory_words_map.values()]
# category_words_array = \
#     [' '.join(words) for words in category_words_map.values()]

from sklearn.feature_extraction.text import TfidfVectorizer
book_vectizer = TfidfVectorizer(max_df=0.65, min_df=0.25, sublinear_tf=True) # 66 books
subcategory_vectizer = TfidfVectorizer(max_df=0.50, min_df=0.0, sublinear_tf=True) # 10 subcats
category_vectizer = TfidfVectorizer() # 2 cats
book_tfidf = \
    book_vectizer.fit_transform(book_words_array)
subcategory_tfidf = \
    subcategory_vectizer.fit_transform(subcategory_words_array)
category_tfidf = \
    category_vectizer.fit_transform(category_words_array)
print("----------- Book TF-IDF --------------")
print(book_vectizer.get_feature_names_out())
print(book_tfidf.shape)
print("----------- Subcategory TF-IDF --------------")
print(subcategory_vectizer.get_feature_names_out())
print(subcategory_tfidf.shape)
print(subcategory_tfidf)
print("----------- Category TF-IDF --------------")
print(category_vectizer.get_feature_names_out())
print(category_tfidf.shape)

def thruplescore(thruple): return thruple[2]
def show_tfidf(name, vectizer, tfidf, doc_names):
    print(f'--------- {name} TF-IDF -------------')
    doc_tuples_map = list()
    for docx, doc_name in enumerate(doc_names):
        tuples = list()
        doc_tuples_map.append(tuples)
        for wordx, word in enumerate(vectizer.get_feature_names_out()):
            score = tfidf[(docx, wordx)]
            if score > 0.01:
                doc_term_tuple = (doc_name, word, score)
                tuples.append(doc_term_tuple)
        tuples.sort(key=thruplescore)
        tuples.reverse()
        for dt_tuple in tuples[:20]:
            print(f'{dt_tuple[0]}\t{dt_tuple[1]}\t{dt_tuple[2]}')
            

show_tfidf('Books', book_vectizer, book_tfidf, asv_constants.BOOKS)
show_tfidf('Subcategories', subcategory_vectizer,
           subcategory_tfidf, asv_constants.SUBCATEGORIES)
show_tfidf('Categories', category_vectizer,
           category_tfidf, asv_constants.CATEGORIES)
# subtuples = list()
# for subx, subcategory in enumerate(subcategories):
#     for wordx, word in enumerate(subcategory_vectizer.get_feature_names_out()):
#         score = subcategory_tfidf[(subx, wordx)]
#         subcategory_tuple = (subcategory, word, score)
#         subtuples.append(subcategory_tuple)

# subtuples.sort(key=thruplescore)
# subtuples.reverse()

# print('top 100 distinguishing terms:')
# for thruple in subtuples[:100]:
#     print(f'{thruple[0]}\t{thruple[1]}\t{thruple[2]}')

