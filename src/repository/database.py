import cx_Oracle

class Database:

    def __init__(self):
        pass

    def select(self, sql):
        conn = cx_Oracle.connect(
            user="TRADING_SODRU", 
            password="TRADING", 
            dsn="10.17.24.2:1521/BPSS") 
        c = conn.cursor()
        c.execute(sql)
        result = []
        for row in c:
            result.append(row)
        c.close()
        return result
