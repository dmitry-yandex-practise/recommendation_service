def retrieve_users_data(conn_ctx_manager):
    with conn_ctx_manager as cur:
        query = cur.mogrify("""
        select id, name from content.users;
        """)
        cur.execute(query)
        users = cur.fetchall()
        print(users[0])
        return users
