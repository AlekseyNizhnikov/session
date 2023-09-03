import sqlite3
import json


class DataBase():
    def __init__(self, name="Journals.db") -> None:
        
        self.connect = sqlite3.connect(name)
        self.cursor = self.connect.cursor()

        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS Journals(
                                                                        journal_id INTEGER PRIMARY KEY,
                                                                        name_journal TEXT,
                                                                        description TEXT);""")

        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS Users(
                                                                    user_id INTEGER PRIMARY KEY,
                                                                    journal_id INTEGER REFERENCES JOURNALS(journal_id) ON UPDATE CASCADE,
                                                                    fname TEXT,
                                                                    lname TEXT,
                                                                    faname TEXT,
                                                                    weight TEXT,
                                                                    height TEXT,
                                                                    age INT,
                                                                    phone TEXT,
                                                                    gender TEXT,
                                                                    img BLOB );""")

        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS Data(
                                                                    data_id INTEGER PRIMARY KEY,
                                                                    user_id INTEGER REFERENCES USERS(user_id) ON UPDATE CASCADE,
                                                                    journal_id INTEGER REFERENCES JOURNALS(journal_id) ON UPDATE CASCADE,
                                                                    session_log TEXT);""")
    

    def set_row(self, name_table:str, data:tuple):
        qwest = '?, ' * len(data)
        self.cursor.executemany(f"""INSERT INTO {name_table} VALUES ({qwest[:-2]});""", [data])
        self.connect.commit()

    def update_row(self, name_table:str, name_col:str, name_id:str, table_id:int, new_data):
        self.cursor.execute(f"""UPDATE {name_table} SET {name_col} = '{new_data}' WHERE {name_id} = '{table_id}';""")
        self.connect.commit()

    def del_row(self, name_tables:list[str], table_id):
        for name_tabel in name_tables:
            self.cursor.execute(f"DELETE FROM {name_tabel} WHERE journal_id='{table_id}';")
        self.connect.commit()

    def get_last_user_id(self, name_table="Users"):
        user_id = self.cursor.execute(f"SELECT user_id FROM {name_table}").fetchall() or 0

        if user_id != 0:
            user_id = user_id[-1][0]

        return user_id
    
    # def get_user_id(self, user_info):
    #     return self.cursor.execute(f"SELECT user_id FROM Users WHERE journal_id = '{journal_id}' AND lname = '{name_user[:-3]}'")

    def get_last_journal_id(self, name_table="Journals"):
        journal_id = self.cursor.execute(f"SELECT journal_id FROM {name_table}").fetchall() or 0

        if journal_id != 0:
            journal_id = journal_id[-1][0]
        return journal_id
    
    def get_last_data_id(self, name_table="Data"):
        data_id = self.cursor.execute(f"SELECT data_id FROM {name_table}").fetchall() or 0

        if data_id != 0:
            data_id = data_id[-1][0]

        return data_id

    def get_journal_id(self, name_journal=None, name_table="Journals"):
        if name_journal:
            return self.cursor.execute(f"SELECT journal_id FROM {name_table} WHERE name_journal = '{name_journal}'").fetchone()[0]
        else:
            return 1
         
    def get_session_log(self, user_id, journal_id, name_table="Data") -> dict:
        session_log = self.cursor.execute(f"""SELECT session_log FROM {name_table} WHERE user_id = '{user_id}' AND journal_id = '{journal_id}';""").fetchone() or None
        if session_log != None:
            session_log = json.loads(session_log[0])
        else:
            session_log = dict()
        return session_log
      
    def get_data_user(self, user_id, journal_id, name_table="Users") -> tuple:
        return self.cursor.execute(f"SELECT * FROM {name_table} WHERE user_id = '{user_id}' AND journal_id = '{journal_id}'").fetchone()

    def get_all_journals(self, name_table="Journals") -> tuple:
        return self.cursor.execute(f"SELECT * FROM {name_table}").fetchall()
    
    def get_all_users(self, journal_id, name_table="Users") -> tuple:
        return self.cursor.execute(f"SELECT * FROM {name_table} WHERE journal_id = '{journal_id}'").fetchall()
    
    def search_journal(self, journal_id, name_journal, name_table = "Journals"):
        journal = self.cursor.execute(f"SELECT journal_id FROM {name_table} WHERE journal_id = '{journal_id}' AND name_journal = '{name_journal}'").fetchone()
        
        if journal != None:
            return False
        return True
