import sqlite3


class DB:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('db.db')
        self.do_setup()

    def do_setup(self) -> None:
        self.conn.execute("CREATE TABLE IF NOT EXISTS 'db_migrations' ('number' INTEGER PRIMARY KEY AUTOINCREMENT)")
        self.conn.commit()
        if self.conn.execute("SELECT COUNT(*) FROM db_migrations").fetchall()[0][0] == 0:
            print("Upgrade version to code 0")
            self.conn.execute("CREATE TABLE 'endpoints' ('id' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 'host' TEXT NOT NULL, 'type' TEXT NOT NULL DEFAULT 'ping')")
            self.conn.execute("CREATE TABLE 'history' ('endpoint' INTEGER NOT NULL, 'startedOn' INTEGER NOT NULL, 'responseTime' INTEGER )")
            self.conn.execute("INSERT INTO db_migrations ('number') VALUES (0)")
        self.conn.commit()

    def get_hosts(self):
        return self.conn.execute("SELECT * FROM endpoints").fetchall()

    def insert_successful_ping(self, endpointID, startedOn, responseTime):
        self.conn.execute("INSERT INTO history (endpoint, startedOn, responseTime) VALUES (?, ?, ?)", (endpointID, startedOn, responseTime))
        self.conn.commit()

    def insert_unsuccessful_ping(self, endpointID, startedOn):
        self.conn.execute("INSERT INTO history (endpoint, startedOn) VALUES (?, ?)", (endpointID, startedOn))
        self.conn.commit()
