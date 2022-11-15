import bz2
import pyarrow as pa
import pyarrow.parquet as pq
import re

import w3hn.hadoop.parquet_util as pq_util
from w3hn.aws.aws_util import S3Util

from w3hn.log.log_init import logger
log = logger(__file__)

COLUMN_NAMES = ['book', 'chapter', 'verse', 'text']
SCHEMA = pa.schema([
    pa.field('book', pa.string()),
    pa.field('chapter', pa.int32()),
    pa.field('verse', pa.int32()),
    pa.field('text', pa.string())
])

asv_bzip_path = 'data/samples/bible-american-standard-version-asv.txt.bz2'
with bz2.open(asv_bzip_path, 'rt') as asv_in:
    lines = asv_in.readlines()
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
            chapter = parts[0][1]
            verse = parts[0][2]
            # print(f'{book}\t{chapter}\t{verse}\t{text}')
            books.append(book)
            chapters.append(chapter)
            verses.append(verse)
            texts.append(text)
    data = [books, chapters, verses, texts]

batch = pa.RecordBatch.from_arrays(data, COLUMN_NAMES)
table = pa.Table.from_batches([batch]).cast(SCHEMA)
log.info(table)

bucket = 'deadmandao'
dataset_path = 'web3hackernetwork/data_pipeline/raw/bible_asv'

s3_util = S3Util(profile='w3hn-admin', bucket_name=bucket)
s3fs = s3_util.pyarrow_fs()
bucket_path = f'{bucket}/{dataset_path}'
log.debug(f'sorting')
table.sort_by([('book', 'ascending'),
               ('chapter', 'ascending'),
               ('verse', 'ascending')])
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
