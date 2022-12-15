import gitinfo as gi

class MyClass():
    def __init__(self):
        self._git = gi.GitInfo()

    def get_git_info(self):
        return self._git.get_info()