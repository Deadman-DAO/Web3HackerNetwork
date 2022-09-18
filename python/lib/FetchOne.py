from db_dependent_class import DBDependent
import base64
import bz2


class FetchOne(DBDependent):
    def __init__(self, **kwargs):
        DBDependent.__init__(self, **kwargs)

    def main(self):
        self.get_cursor().execute('select numstat from repo_numstat where id = 181324')
        result = self.get_cursor().fetchone()
        binary = base64.b64decode(result[0])
        bz2.decompress(binary)
        raw_numstat = bz2.decompress(binary)
        with open("181324.json", "wb") as f:
            f.write(raw_numstat)


if __name__ == '__main__':
    FetchOne().main()