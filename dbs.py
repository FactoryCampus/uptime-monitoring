import sqlite3
import datetime


def dict_factory(cursor, row):
    d = {}
    for con, col in enumerate(cursor.description):
        d[col[0]] = row[con]
    return d


class DB:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('db.db')
        self.do_setup()
        self.conn.row_factory = dict_factory

    def do_setup(self) -> None:
        self.conn.execute("CREATE TABLE IF NOT EXISTS 'db_migrations' ('number' INTEGER PRIMARY KEY AUTOINCREMENT)")
        self.conn.commit()
        version = self.conn.execute("SELECT COUNT(*) FROM db_migrations").fetchall()[0][0]
        if version == 0:
            print("Upgrade version to code 0")
            self.conn.execute("CREATE TABLE 'endpoints' ('id' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 'host' TEXT NOT NULL, 'type' TEXT NOT NULL DEFAULT 'ping')")
            self.conn.execute("CREATE TABLE 'history' ('endpoint' INTEGER NOT NULL, 'startedOn' INTEGER NOT NULL, 'responseTime' INTEGER )")
            self.conn.execute("INSERT INTO db_migrations ('number') VALUES (0)")
        if version <= 1:
            print("Upgrade version to code 1")
            self.conn.execute("ALTER TABLE endpoints ADD alias TEXT")
            self.conn.execute("INSERT INTO db_migrations ('number') VALUES (1)")
        if version <= 2:
            print("Upgrade version to code 2")
            self.conn.execute("ALTER TABLE endpoints ADD active DEFAULT TRUE")
            self.conn.execute("INSERT INTO db_migrations ('number') VALUES (2)")
        if version <= 3:
            print("Upgrade version to code 3")
            self.conn.execute("ALTER TABLE endpoints ADD interval integer NOT NULL DEFAULT 60")
            self.conn.execute("INSERT INTO db_migrations ('number') VALUES (3)")
        self.conn.commit()

    def get_hosts(self, only_active=False):
        return self.conn.execute("SELECT * FROM endpoints" + (' WHERE active' if only_active else '')).fetchall()

    def update_endpoint(self, id, host, alias, interval, active):
        self.conn.execute("UPDATE endpoints SET host=?, alias=?, active=?, interval=? WHERE id=?", (host, alias, active, interval, id))
        self.conn.commit()

    def add_endpoint_host(self, host, alias):
        self.conn.execute("INSERT INTO endpoints (host, alias) VALUES (?, ?)", (host, alias))
        self.conn.commit()

    def insert_successful_ping(self, endpointID, startedOn, responseTime):
        self.conn.execute("INSERT INTO history (endpoint, startedOn, responseTime) VALUES (?, ?, ?)", (endpointID, startedOn, responseTime))
        self.conn.commit()

    def insert_unsuccessful_ping(self, endpointID, startedOn):
        self.conn.execute("INSERT INTO history (endpoint, startedOn) VALUES (?, ?)", (endpointID, startedOn))
        self.conn.commit()

    def get_unsuccessful_connections_today(self):
        return self.conn.execute("SELECT ifnull(alias, host) as host, startedOn FROM history JOIN endpoints ON history.endpoint = endpoints.id WHERE responseTime IS NULL AND startedOn > ?", (datetime.date.today().strftime("%s"), )).fetchall()
