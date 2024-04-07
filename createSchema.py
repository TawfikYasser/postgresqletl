import psycopg2

from sqlQueries import create_table_holder, drop_table_holder

def create_database():

    """
    1. Create the sparkify DB.
    2. Connect to the sparkify DB.
    2. Return the connection and cursor to the sparkify DB.
    """

    # Connect to the default database
    conn = psycopg2.connect("host=172.23.0.3 dbname=postgres user=postgres password=P@ssw0rd")
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    # Create the sparkifydb
    cur.execute("DROP DATABASE IF EXISTS sparkifydb")
    cur.execute("CREATE DATABASE sparkifydb WITH ENCODING 'utf8' TEMPLATE template0")


    # Close the connection with the default db
    conn.close()

    # Connect to the sparkifydb
    conn = psycopg2.connect("host=172.23.0.3 dbname=sparkifydb user=postgres password=P@ssw0rd")
    cur = conn.cursor()

    return cur, conn


def drop_tables(cur, conn):
    """
    DROP ALL TABLES in the drop tables holder from the sqlQueries.py
    """

    for query in drop_table_holder:
        cur.execute(query)
        conn.commit()

def create_tables(cur, conn):
    """
    CREATE ALL TABLES in the create tables holder from the sqlQueries.py
    """

    for query in create_table_holder:
        cur.execute(query)
        conn.commit()


def main():
    """
    1. CREATE sparkify DB and connect to it and get a cursor to it.
    2. DROP ALL TABLES (IF EXISTS)
    3. CREATE ALL TABLES
    4. Close the connection
    """

    cur, conn = create_database()

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()

if __name__ == "__main__":
    main()