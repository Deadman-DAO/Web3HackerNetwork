OT = ['Genesis', 'Exodus', 'Leviticus', 'Numbers',
      'Deuteronomy', 'Joshua', 'Judges', 'Ruth', '1 Samuel',
      '2 Samuel', '1 Kings', '2 Kings', '1 Chronicles',
      '2 Chronicles', 'Ezra', 'Nehemiah', 'Esther', 'Job',
      'Psalms', 'Proverbs', 'Ecclesiastes', 'Song of Solomon',
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

SUBCATEGORY_BOOK_MAP = {
    'moses school': ['Genesis', 'Exodus', 'Leviticus',
                     'Numbers', 'Deuteronomy'],
    'history': ['Joshua', 'Judges', 'Ruth', '1 Samuel',
                '2 Samuel', '1 Kings', '2 Kings',
                '1 Chronicles', '2 Chronicles', 'Ezra',
                'Nehemiah', 'Esther', 'Job'],
    'poetry': ['Psalms'],
    'wisdom literature': ['Proverbs',
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

CATEGORIES = ['old testament', 'new testament']
SUBCATEGORIES = list(SUBCATEGORY_BOOK_MAP.keys())
BOOKS = OT + NT
