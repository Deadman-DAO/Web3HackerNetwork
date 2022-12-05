import re
import os
import traceback
from lib.monitor import timeit
from w3hn.dependency.analyzer import DependencyAnalyzer

_start_comment_block = '/*'
_end_comment_block = '*/'
_comment_out_line = '//'
_import = "include"
_import = "#include"
_open_bracket = "<"
_close_bracket = ">"
_quote = '"'


class CDependency(DependencyAnalyzer):

    def __init__(self):
        self.depends = list()
        self.source_code_encountered = False
        self.comment_block_started = False
        self.import_started = False
        self.import_paren_started = False
        self.first_import_word_found = False

    def language(self):
        return "C/CPP"

    def matches(self, path):
        return path.endswith('.c', '.cpp', '.h', '.hpp')

    def analyze_word(self, word):
        if self.comment_block_started:
            if word and word.endswith(_end_comment_block):
                self.comment_block_started = False
        elif self.import_started:
            self.source_code_encountered = True
            if word.startswith(_open_bracket):
                if self.import_paren_started:
                    raise Exception('Duplicate open parenthesis found!')
                self.import_paren_started = True
                if len(word) > 1:
                    self.analyze_word(word[1:])
            elif word.startswith(_quote):
                # This is the actual import
                impy = word[1:word.find('"', 1)]
                self.depends.append(impy)
                if word.endswith(_quote):
                    self.import_started = False
                    self.import_paren_started = False
                elif not self.import_paren_started:
                    # done with this import
                    self.import_started = False
            elif word.endswith(_close_bracket):
                self.import_started = False
                self.import_paren_started = False
        elif word == _import:
            if self.source_code_encountered:
                raise Exception("'import' must be the first word on the line: ", word)
            self.import_started = True
            self.source_code_encountered = True
        elif word.startswith(_start_comment_block):
            self.comment_block_started = True
            if len(word) > len(_start_comment_block):
                self.analyze_word(word[len(_start_comment_block):])
        elif word.endswith(_end_comment_block):
            self.comment_block_started = False


    @timeit
    def get_dependencies(self, path):
        disable = 'DISABLE_GO_DEPENDENCIES'
        if disable in os.environ.keys() and os.environ[disable]:
            return list()

        self.__init__()

        try:
            with open(path, 'r') as go_source:
                try:
                    last_line = None
                    for c_line in go_source:
                        last_line = c_line
                        c_line = re.sub("//.*", "", c_line) # Eliminates // comments until end of line
                        self.source_code_encountered = False
                        for word in re.split("(?:[\s])+", c_line):
                            if len(word) > 0:
                                self.analyze_word(word)
                except Exception as e:
                    print(e, 'encountered processing file: ', path, 'line: ', last_line)

        except Exception as e:
            print(e, 'encountered opening file: ', path)
            traceback.print_exception(e)

        return self.depends


if __name__ == '__main__':
    dep = CDependency()
    print(dep.get_dependencies('./featureVector.cpp'))
