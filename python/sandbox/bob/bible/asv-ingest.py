import bz2

asv_bzip_path = 'data/samples/bible-american-standard-version-asv.txt.bz2'
with bz2.open(asv_bzip_path, 'rt') as asv_in:
    lines = asv_in.readlines()
    for line in lines[:10]:
        parts = line[:-1].split('\t')
        if len(parts) == 2:
            book_space_chapter_colon_verse = parts[0]
            verse_text = parts[1]
            print(f'{book_space_chapter_colon_verse}\t{verse_text}')

