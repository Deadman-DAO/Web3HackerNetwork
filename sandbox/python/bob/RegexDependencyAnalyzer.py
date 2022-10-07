import re

class RegexDependencyAnalyzer():
    def __init__(self, language, suffixen, regex):
        self.language = language
        self.suffixen = suffixen
        self.regex = regex
        self.pattern = re.compile(regex)

    def analyze(self, filepath):
        # print('analyzing ' + str(filepath))
        file1 = open(filepath, 'r')
        lines = file1.readlines()
        for line in lines:
            matches = self.pattern.findall(line)
            for match in matches:
                print(match)
#


# foo = RegexDependencyAnalyzer("Rust", ["rs"], "^use ([^[;:]]*)[;:]");
foo = RegexDependencyAnalyzer("Rust", ["rs"], "^use ([^:^;]*)[;:].*$");
foo.analyze("main.rs");

bar = RegexDependencyAnalyzer("Java", ["java"], "^import ([^;]*);$");
bar.analyze("SpotifyApi.java");
