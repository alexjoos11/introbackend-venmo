import os
import sqlite3

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for Venmo app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        """
        Secures a connection with the database and stores int into the instance variable 'conn'
        """
        self.conn = sqlite3.connect(
            "todo.db", check_same_thread=False
            )
        self.create_user_table()

    def create_user_table(self):
        """
        Using SQL, creates a user table
        """
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS user (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL,
                          username TEXT NOT NULL,
                          balance INTEGER NOT NULL DEFAULT 0
        );
        """)

    def delete_user_table(self):
        """
        Using SQL, delete the USER table
        """
        self.conn.execute("DROP TABLE IF EXISTS user;")

    def get_all_users(self):
        """
        Using SQL, get all users in the table
        """
        cursor = self.conn.execute("SELECT * FROM user;")
        users = []
        for row in cursor:
            users.append({"id": row[0], "name":row[1], "username":row[2]})
        return users
    
    def insert_user_table(self, name, username, balance=0):
        """
        Using SQL, create a user
        """
        cursor = self.conn.execute("INSERT INTO user (name, username, balance) VALUES (?, ?, ?)", (name, username, balance))
        self.conn.commit() #committing is actually writing to the database
        return cursor.lastrowid #returns the row that you created

    def get_user_by_id(self,id):
        """
        Using SQL, get a user by its id
        """
        cursor = self.conn.execute("SELECT * FROM user WHERE id = ?;", (id,)) #the comma after id is important cause it has to be a tuple
        for row in cursor:
            return {"id":row[0], "name":row[1], "username":row[2], "balance":row[3]}
        return None #if cursor is empty then we skip the for loop and return None

    def delete_user_by_id(self, id):
        """
        Using SQL, deletes a user from our table
        """
        self.conn.execute("DELETE FROM user WHERE id = ?", (id,))
        self.conn.commit()

    def transfer_balance_by_id(self, sender_id, receiver_id, amount):
        """
        Using SQL, transfer [amount] from the balance of [sender_id] to the balance of [receiver_id]
        """
        cursor = self.conn.execute("SELECT balance FROM user WHERE id=?;", (sender_id,))
        sender_balance = cursor.fetchone()[0]
        cursor = self.conn.execute("SELECT balance FROM user WHERE id=?;", (receiver_id,))
        receiver_balance = cursor.fetchone()[0]

        self.conn.execute("""
        UPDATE user
        SET balance = ?
        WHERE id = ?;
        """,
        (sender_balance - amount, sender_id)
        )
        self.conn.execute("""
        UPDATE user
        SET balance = ?
        WHERE id = ?;
        """,
        (receiver_balance + amount, receiver_id)
        )
        self.conn.commit()


# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
