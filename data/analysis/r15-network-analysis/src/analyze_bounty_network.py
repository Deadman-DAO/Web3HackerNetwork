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

def load_poap_like_network(conn):
    G = nx.Graph()
    cursor = conn.cursor()
    sql = "select left_bounty_pk, right_bounty_pk" \
        + " from bounty_fulfillment_matrix m" \
        + " where weight >= 3" \
        + " and exists ( select 1 from poap_like p" \
        + "   where p.pk = m.left_bounty_pk )" \
        + " and exists ( select 1 from poap_like p" \
        + "   where p.pk = m.right_bounty_pk )"
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

def load_poap_network(conn):
    G = nx.Graph()
    cursor = conn.cursor()
    sql = "select left_bounty_pk, right_bounty_pk" \
        + " from bounty_fulfillment_matrix m" \
        + " where 1 = 1" \
        + " and exists ( select 1 from gitcoin_raw.bounty b" \
        + "   where b.pk = m.left_bounty_pk" \
        + "   and b.title like '%poap%' )" \
        + " and exists ( select 1 from gitcoin_raw.bounty b" \
        + "   where b.pk = m.right_bounty_pk" \
        + "   and b.title like '%poap%' )"
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

def load_non_poap_network(conn):
    G = nx.Graph()
    cursor = conn.cursor()
    sql = "select left_bounty_pk, right_bounty_pk" \
        + " from bounty_fulfillment_matrix m" \
        + " where 1 = 1 " \
        + " and not exists ( select 1 from gitcoin_raw.bounty b" \
        + "   where b.pk = m.left_bounty_pk" \
        + "   and b.title like '%poap%' )" \
        + " and not exists ( select 1 from gitcoin_raw.bounty b" \
        + "   where b.pk = m.right_bounty_pk" \
        + "   and b.title like '%poap%' )"
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

def load_non_poap_like_network(conn):
    G = nx.Graph()
    cursor = conn.cursor()
    sql = "select left_bounty_pk, right_bounty_pk" \
        + " from bounty_fulfillment_matrix m" \
        + " where weight >= 3" \
        + " and not exists ( select 1 from poap_like p" \
        + "   where p.pk = m.left_bounty_pk )" \
        + " and not exists ( select 1 from poap_like p" \
        + "   where p.pk = m.right_bounty_pk )"
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

def load_network(conn):
    G = nx.Graph()
    cursor = conn.cursor()
    sql = "select left_bounty_pk, right_bounty_pk" \
        + " from bounty_worked_matrix" \
        + " where weight >= 3"
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

def load_non_poap_user_network(conn):
    G = nx.Graph()
    cursor = conn.cursor()
    sql = "select left_profile_id, right_profile_id" \
        + " from user_non_poap_matrix" \
        + " where weight >= 2"
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
        sql = "INSERT INTO bounty_centrality" \
            " (bounty_pk, centrality) values (?, ?)"
        data = ( key, val )
        cursor.execute(sql, data, True)
    conn.commit()
    return

def record_non_poap_centrality(conn, G):
    centrality = nx.degree_centrality(G)
    cursor = conn.cursor()
    for key in centrality:
        val = centrality.get(key)
        sql = "INSERT INTO bounty_non_poap_centrality" \
            " (bounty_pk, centrality) values (?, ?)"
        data = ( key, val )
        cursor.execute(sql, data, True)
    conn.commit()
    return

def main():
    password = getpass.getpass("password (password): ")
    conn = connect( "w3hn", password, "localhost", "gitcoin_matrices")
    G = load_poap_network(conn)
    # G = load_poap_like_network(conn)
    # G = load_non_poap_network(conn)
    # G = load_non_poap_like_network(conn)
    
    # G = load_non_poap_user_network(conn)
    if (False): record_non_poap_centrality(conn, G)
    conn.close()
    
    print("density: ", nx.density(G))
    print("assortativity: ", nx.degree_assortativity_coefficient(G))
    return

main()


# Non-POAP-Like
# $ python3 src/analyze_bounty_network.py 
# select left_bounty_pk, right_bounty_pk from bounty_fulfillment_matrix m where weight >= 3 and not exists ( select 1 from poap_like p   where p.pk = m.left_bounty_pk ) and not exists ( select 1 from poap_like p   where p.pk = m.right_bounty_pk )
# density:  0.004779776235660671
# assortativity:  -0.32297278263111184

# POAP-Like
# $ python3 src/analyze_bounty_network.py 
# select left_bounty_pk, right_bounty_pk from bounty_fulfillment_matrix m where weight >= 3 and exists ( select 1 from poap_like p   where p.pk = m.left_bounty_pk ) and exists ( select 1 from poap_like p   where p.pk = m.right_bounty_pk )
# density:  0.41647940074906364
# assortativity:  0.777499759648589

# POAP Network
# $ python3 src/analyze_bounty_network.py 
# select left_bounty_pk, right_bounty_pk from bounty_fulfillment_matrix m where weight >= 3 and exists ( select 1 from gitcoin_raw.bounty b   where b.pk = m.left_bounty_pk   and b.title like '%poap%' ) and exists ( select 1 from gitcoin_raw.bounty b   where b.pk = m.right_bounty_pk   and b.title like '%poap%' )
# density:  0.9167437557816837
# assortativity:  0.9999999999997046

# Non-POAP
# $ python3 src/analyze_bounty_network.py 
# select left_bounty_pk, right_bounty_pk from bounty_fulfillment_matrix m where weight >= 3 and not exists ( select 1 from gitcoin_raw.bounty b   where b.pk = m.left_bounty_pk   and b.title like '%poap%' ) and not exists ( select 1 from gitcoin_raw.bounty b   where b.pk = m.right_bounty_pk   and b.title like '%poap%' )
# density:  0.005797764809093336
# assortativity:  -0.3092877083506619
