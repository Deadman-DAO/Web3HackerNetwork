from git import Repo

class MyClass():
    def __init__(self):
        self._git = Repo('.')

    def get_git_info(self):
        return self._git.blame('README.md')

if __name__ == '__main__':
    mc = MyClass()
    print(mc.get_git_info())