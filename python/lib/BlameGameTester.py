from repo_analyzer import BlameGameRetriever
from monitor import MultiprocessMonitor


def main():
    repo_dir = './repos/Lexxie9952/fcw.org-server'
    file_name = './freeciv-web/src/main/webapp/images/e/musketeers.png'
    commit_author_map = {}
    bgr = BlameGameRetriever(repo_dir, commit_author_map)
    dic = bgr.get_blame_game(file_name)
    print(dic)


if __name__ == '__main__':
    main()
