import networkx as nx
import mariadb as db
import getpass

def introspect(obj):
    print(type(obj))
    print(dir(obj))
    return

def connect(user, password, host, database):
    conn_params = { "user": user, "password": password,
        "host": host, "database": database }
    conn = db.connect(**conn_params)
    return conn

def load_network(conn):
    G = nx.Graph()
    cursor = conn.cursor()
    sql = "select left_profileId, right_profileId" \
        + " from user_sparse_matrix" \
        + " where weight >= 1"
    print(sql)
    cursor.execute(sql)
    row = cursor.fetchone()
    while (row):
        G.add_node(row[0])
        G.add_node(row[1])
        G.add_edge(row[0], row[1])
        row = cursor.fetchone()
    cursor.close()
    return G

def record_centrality(conn, G):
    centrality = nx.degree_centrality(G)
    cursor = conn.cursor()
    for key in centrality:
        val = centrality.get(key)
        sql = "INSERT INTO centrality" \
            " (profileId, centrality) values (?, ?)"
        data = ( key, val )
        cursor.execute(sql, data, True)
    conn.commit()
    return

def main():
    password = getpass.getpass("password (password): ")
    conn = connect( "gitcoin-test", password, "localhost", "gitcoin_test")
    G = load_network(conn)
    if (False): record_centrality(conn, G)
    conn.close()
    
    print("density: ", nx.density(G))
    print("assortativity: ", nx.degree_assortativity_coefficient(G))
    return

main()
