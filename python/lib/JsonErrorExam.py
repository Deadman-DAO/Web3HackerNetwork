import base64
import bz2
import json

from db_dependent_class import DBDependent


class JsonErrorExam(DBDependent):
    def __init__(self):
        DBDependent.__init__(self)

    def main(self):
        self.get_cursor().execute("select numstat from repo_numstat where id = 516")
        for row in self.cursor:
            binary = base64.b64decode(row[0])
            raw_numstat = bz2.decompress(binary)
            with open("516.json", "wb") as f:
                f.write(raw_numstat)
            try:
                numstat = json.loads(raw_numstat)
            except Exception as e:
                print(e, 'trying again with ] on the tail')
                ba = bytearray(raw_numstat)
                ba.append(93)
                numstat = json.loads(ba)
            print('Not dead yet!', len(numstat))
            print(numstat)


if __name__ == '__main__':
    JsonErrorExam().main()
    print('Done')
    exit()