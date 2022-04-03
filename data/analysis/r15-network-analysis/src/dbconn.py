import networkx as nx
import mariadb as db
import matplotlib.pyplot as plt
import getpass

def record_centrality(conn, G):
    centrality = nx.degree_centrality(G)
    print(type(centrality))
    print(dir(centrality))
    cursor = conn.cursor()
    for key in centrality:
        val = centrality.get(key)
        sql = "INSERT INTO centrality" \
            " (profileId, centrality) values (?, ?)"
        data = ( key, val )
        cursor.execute(sql, data, True)
        # print(key, " ", val)
    
    conn.commit()

def connect(user, password, host, database):
    conn_params = {
        "user": user,
        "password": password,
        "host": host,
        "database": database
    }
    conn = db.connect(**conn_params)
    return conn

pwd = getpass.getpass("password: ")
conn = connect( "gitcoin-test", pwd, "localhost", "gitcoin_test")
# cursor = conn.cursor()
# # sql = "select pk, url, title from bounty where pk < ? limit 10"
# # data = ( 123456 )
# # cursor.execute(sql, data)
# sql = "select pk, url, title from bounty where pk < 123456 limit 10"
# cursor.execute(sql)
# row = cursor.fetchone()
# print(row[0], row[1], row[2])
# while (row):
#     print(*row, sep="\t")
#     row = cursor.fetchone()
# cursor.close()

