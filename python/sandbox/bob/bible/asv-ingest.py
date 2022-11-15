import bz2
import pyarrow as pa
import pyarrow.parquet as pq
import re

import w3hn.hadoop.parquet_util as pq_util
from w3hn.aws.aws_util import S3Util

from w3hn.log.log_init import logger
log = logger(__file__)

OT = ['Genesis', 'Exodus', 'Leviticus', 'Numbers',
      'Deuteronomy', 'Joshua', 'Judges', 'Ruth', '1 Samuel',
      '2 Samuel', '1 Kings', '2 Kings', '1 Chronicles',
      '2 Chronicles', 'Ezra', 'Nehemiah', 'Esther', 'Job',
      'Psalm', 'Proverbs', 'Ecclesiastes', 'Song of Solomon',
      'Isaiah', 'Jeremiah', 'Lamentations', 'Ezekiel',
      'Daniel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah',
      'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai',
      'Zechariah', 'Malachi']

NT = ['Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans',
      '1 Corinthians', '2 Corinthians', 'Galatians',
      'Ephesians', 'Philippians', 'Colossians',
      '1 Thessalonians', '2 Thessalonians', '1 Timothy',
      '2 Timothy', 'Titus', 'Philemon', 'Hebrews', 'James',
      '1 Peter', '2 Peter', '1 John', '2 John', '3 John',
      'Jude', 'Revelation']

SUBCATEGORIES = {
    'moses school': ['Genesis', 'Exodus', 'Leviticus',
                     'Numbers', 'Deuteronomy'],
    'history': ['Joshua', 'Judges', 'Ruth', '1 Samuel',
                '2 Samuel', '1 Kings', '2 Kings',
                '1 Chronicles', '2 Chronicles', 'Ezra',
                'Nehemiah', 'Esther', 'Job'],
    'wisdom literature': ['Psalm', 'Proverbs',
                          'Ecclesiastes', 'Song of Solomon'],
    'major prophets': ['Isaiah', 'Jeremiah', 'Lamentations',
                       'Ezekiel', 'Daniel'],
    'minor prophets': ['Hosea', 'Joel', 'Amos', 'Obadiah',
                       'Jonah', 'Micah', 'Nahum', 'Habakkuk',
                       'Zephaniah', 'Haggai', 'Zechariah',
                       'Malachi'],
    'gospel': ['Matthew', 'Mark', 'Luke', 'John'],
    'after ascension': ['Acts'],
    'letters': [
        'Romans', '1 Corinthians', '2 Corinthians', 'Galatians',
        'Ephesians', 'Philippians', 'Colossians',
        '1 Thessalonians', '2 Thessalonians', '1 Timothy',
        '2 Timothy', 'Titus', 'Philemon', 'Hebrews', 'James',
        '1 Peter', '2 Peter', '1 John', '2 John', '3 John',
        'Jude'
    ],
    'apocalyptic literature': ['Revelation']
}

COLUMN_NAMES = ['religion', 'tome', 'version', 'category',
                'subcategory', 'book', 'chapter', 'verse', 'text']
SCHEMA = pa.schema([
    pa.field('religion', pa.string()),
    pa.field('tome', pa.string()),
    pa.field('version', pa.string()),
    pa.field('category', pa.string()),
    pa.field('subcategory', pa.string()),
    pa.field('book', pa.string()),
    pa.field('chapter', pa.int32()),
    pa.field('verse', pa.int32()),
    pa.field('text', pa.string())
])

asv_bzip_path = 'data/samples/bible-american-standard-version-asv.txt.bz2'
with bz2.open(asv_bzip_path, 'rt') as asv_in:
    lines = asv_in.readlines()
    religions = []
    tomes = []
    versions = []
    categories = []
    subcategories = []
    books = []
    chapters = []
    verses = []
    texts = []
    for line in lines:#[:10]:
        parts = line[:-1].split('\t')
        if len(parts) == 2:
            book_ch_verse = parts[0]
            text = parts[1]
            parts = re.findall('^(.*) ([0-9]*):([0-9]*)$', book_ch_verse)
            book = parts[0][0]
            if book in OT:
                testament = 'old testament'
            else:
                testament = 'new testament'
            chapter = parts[0][1]
            verse = parts[0][2]
            # print(f'{book}\t{chapter}\t{verse}\t{text}')
            religions.append('protestant')
            tomes.append('bible')
            versions.append('asv')
            categories.append(testament)
            book_subcategory = 'unknown'
            for subcategory, member_books in SUBCATEGORIES.items():
                if book in member_books:
                    # print(f'{book} = {subcategory}: {member_books}')
                    book_subcategory = subcategory
            subcategories.append(book_subcategory)
            books.append(book)
            chapters.append(chapter)
            verses.append(verse)
            texts.append(text)
    data = [religions, tomes, versions, categories, subcategories,
            books, chapters, verses, texts]

batch = pa.RecordBatch.from_arrays(data, COLUMN_NAMES)
table = pa.Table.from_batches([batch]).cast(SCHEMA)
log.info(table)

bucket = 'deadmandao'
dataset_path = 'web3hackernetwork/data_pipeline/raw/bible_asv'

s3_util = S3Util(profile='w3hn-admin', bucket_name=bucket)
s3fs = s3_util.pyarrow_fs()
bucket_path = f'{bucket}/{dataset_path}'
# log.debug(f'sorting')
# table.sort_by([('religion', 'ascending'),
#                ('tome', 'descending'),
#                ('version', 'descending'),
#                ('category', 'descending'),
#                ('subcategory', 'descending'),
#                ('book', 'ascending'),
#                ('chapter', 'ascending'),
#                ('verse', 'ascending')])
log.info(f'writing {bucket}/{dataset_path}')
if s3_util.path_exists(dataset_path):
    log.info(f'deleting {bucket}/{dataset_path}')
    s3fs.delete_dir(f'{bucket}/{dataset_path}')
else:
    log.info(f'no delete at {bucket}/{dataset_path}')
# table.coalesce(1)
pq.write_to_dataset(table,
                    root_path=bucket_path,
                    # partition_cols=['partition_key'],
                    filesystem=s3fs)
log.info(f'write complete')
