import os
from w3hn.dependency.golang import GoDependencyAnalyzer


class GoTester:
    def __init__(self, file_name='go_test.sample'):
        self.root_dir_name = 'Web3HackerNetwork'
        self.test_sample = file_name

    def test_it(self):
        dir = os.path.abspath(os.path.join(__file__, os.pardir))
        sample_file = os.path.join(dir, self.test_sample)
        assert os.path.exists(sample_file)
        dependencies = GoDependencyAnalyzer().get_dependencies(sample_file)
        print(dependencies)


if __name__ == '__main__':
    GoTester('M:\\Projects\\new\\Web3HackerNetwork\\active\\repos\\u-root\\u-root\\uroot_test.go').test_it()