import sqlite3

DB_NAME = "invernadero.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id TEXT PRIMARY KEY,
            fecha TEXT,
            categoria TEXT,
            detalle TEXT,
            foto TEXT
        )
    ''')
    conn.commit()
    conn.close()

def ejecutar(query, params=()):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def consultar(query, params=()):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    conn.close()
    return resultados
