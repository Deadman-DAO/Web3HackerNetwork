import networkx as nx
import mariadb as db
import matplotlib.pyplot as plt
import getpass

def record_centrality(conn, G):
    centrality = nx.degree_centrality(G)
    # print(type(centrality))
    # print(dir(centrality))
    cursor = conn.cursor()
    for key in centrality:
        val = centrality.get(key)
        sql = "INSERT INTO centrality" \
            " (profileId, centrality) values (?, ?)"
        data = ( key, val )
        cursor.execute(sql, data, True)
    conn.commit()

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
        leftId = row[0]
        rightId = row[1]
        G.add_node(leftId)
        G.add_node(rightId)
        G.add_edge(leftId, rightId)
        row = cursor.fetchone()
    cursor.close()
    return G

password = getpass.getpass("password: ")
conn = connect( "gitcoin-test", password, "localhost", "gitcoin_test")
if (False): record_centrality(conn, G)

print("density: ", nx.density(G))
print("assortativity: ", nx.degree_assortativity_coefficient(G))


# nodes = G.nodes()
# print(type(nodes))
# print(dir(nodes))
# # print(nodes.keys())
# print(type(G))
# print(dir(G))

# # nx.draw(G) #, with_labels=True, font_weight='bold')
# # plt.savefig("foo.png")


# # node_opts = {"node_size": 10}
# # pos = nx.circular_layout(G)
# # nx.draw_networkx_nodes(G, pos, **node_opts)
# # nx.draw_networkx_edges(G, pos)
# # plt.show()
# # # plt.savefig("foo.png")

conn.close()


