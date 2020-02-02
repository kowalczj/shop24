import sqlite3

conn = sqlite3.connect('shop24.db')

c = conn.cursor()

c.execute("""DROP TABLE IF EXISTS accounts""")

c.execute("""CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            fname TEXT NOT NULL,
            lname TEXT NOT NULL,
            email TEXT NOT NULL,
            street TEXT NOT NULL,
            city TEXT NOT NULL
            )""")

c.execute("""DROP TABLE IF EXISTS orders""")

c.execute("""CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            account_id INTEGER NOT NULL,
            DATE TEXT NOT NULL,
            FOREIGN KEY (account_id)
                REFERENCES accounts (account_id)
            )""")

c.execute("""DROP TABLE IF EXISTS categories""")

c.execute("""CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY,
            category_name TEXT
            )""")


c.execute("""DROP TABLE IF EXISTS products""")

c.execute("""CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price INTEGER NOT NULL,
            category_id INTEGER,
            FOREIGN KEY (category_id)
                REFERENCES categories (category_id)
            )""")

c.execute("""DROP TABLE IF EXISTS orders_products""")

c.execute("""CREATE TABLE IF NOT EXISTS orders_products (
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            PRIMARY KEY (order_id, product_id),
            FOREIGN KEY (order_id)
                REFERENCES orders (order_id),
            FOREIGN KEY (product_id)
                REFERENCES products (product_id)
            )""")

c.execute("""DROP TABLE IF EXISTS reviews""")

c.execute("""CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            account_id INTEGER NOT NULL,
            rating INTEGER,
            review BLOB,
            FOREIGN KEY (product_id)
                REFERENCES products (product_id),
            FOREIGN KEY (account_id)
                REFERENCES accounts (account_id)
            )""")

conn.commit()
conn.close()
