import sqlite3



class Database:
    def __init__(self, name = 'db.sqlite'):
        self.dbname = name
        with sqlite3.connect(self.dbname) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS results(
                            RSSI TEXT,
                            SINR TEXT,
                            RSRQ TEXT,
                            RSRP TEXT,
                            MOS REAL,
                            ts TIMESTAMP
                        );
            """)
            conn.commit()

    def add_record(self, rssi, sinr, rsrq, rsrp, mos, ts):

        sql = "INSERT INTO results(RSSI,SINR,RSRQ,RSRP,MOS,ts) VALUES (?,?,?,?,?,?);"
        with sqlite3.connect(self.dbname) as conn:
            conn.execute(sql, (rssi, sinr, rsrq, rsrp, mos, ts))
            conn.commit()

    