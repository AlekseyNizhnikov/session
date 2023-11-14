from configurate.database import _NAME_USERS_DATABASE, _NAME_DATA_DATABASE, _NAME_DATABASE, _NAME_JOURNALS_DATABASE, _NAME_SETTINGS_JOURNAL, _NAME_EVENTS_JOURNAL, _NAME_TASK_EVENT
import sqlite3
import json


class DataBase():
    def __init__(self, name=_NAME_DATABASE) -> None:
        self.connect = sqlite3.connect(f"controller/{name}")
        self.cursor = self.connect.cursor()

        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {_NAME_JOURNALS_DATABASE}(
                                                                    journal_id INTEGER PRIMARY KEY,
                                                                    name_journal TEXT,
                                                                    description TEXT);""")
        
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {_NAME_SETTINGS_JOURNAL}(
                                                                    config_id INTEGER PRIMARY KEY,
                                                                    journal_id INTEGER REFERENCES JOURNALS(journal_id) ON UPDATE CASCADE,
                                                                    config TEXT);""")
        
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {_NAME_USERS_DATABASE}(
                                                                    user_id INTEGER PRIMARY KEY,
                                                                    journal_id INTEGER REFERENCES JOURNALS(journal_id) ON UPDATE CASCADE,
                                                                    fname TEXT,
                                                                    lname TEXT,
                                                                    faname TEXT,
                                                                    weight TEXT,
                                                                    height TEXT,
                                                                    age INT,
                                                                    phone TEXT,
                                                                    birthday TEXT,
                                                                    gender TEXT,
                                                                    img BLOB );""")
        
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {_NAME_DATA_DATABASE}(
                                                                    data_id INTEGER PRIMARY KEY,
                                                                    user_id INTEGER REFERENCES USERS(user_id) ON UPDATE CASCADE,
                                                                    journal_id INTEGER REFERENCES JOURNALS(journal_id) ON UPDATE CASCADE,
                                                                    session_log TEXT);""")
        
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {_NAME_EVENTS_JOURNAL}(
                                                                    event_id INTEGER PRIMARY KEY,
                                                                    journal_id INTEGER REFERENCES JOURNALS(journal_id) ON UPDATE CASCADE,
                                                                    switch_period BOOL,
                                                                    switch_task BOOL,
                                                                    period INT,
                                                                    date TEXT,
                                                                    task_1 TEXT,
                                                                    task_2 TEXT,
                                                                    task_3 TEXT,
                                                                    task_4 TEXT,
                                                                    task_5 TEXT,
                                                                    task_6 TEXT,
                                                                    task_7 TEXT,
                                                                    task_8 TEXT,
                                                                    task_9 TEXT,
                                                                    task_10 TEXT );""")
    
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {_NAME_TASK_EVENT}(
                                                                    task_id INTEGER PRIMARY KEY,
                                                                    event_id INTEGER REFERENCES EventsJournals(event_id) ON UPDATE CASCADE,
                                                                    task TEXT);""")

    def set_row(self, name_table:str, data:tuple):
        qwest = '?, ' * len(data)
        self.cursor.executemany(f"""INSERT INTO {name_table} VALUES ({qwest[:-2]});""", [data])
        self.connect.commit()

    def del_row(self, name_tables:list[str], journal_id:str):
        for name_tabel in name_tables:
            self.cursor.execute(f"DELETE FROM {name_tabel} WHERE journal_id='{journal_id}';")
        self.connect.commit()

    def del_row_user(self, user_id:str, journal_id:str):
        self.cursor.execute(f"DELETE FROM Users WHERE journal_id='{journal_id}' AND user_id = '{user_id}';")
        self.connect.commit()

    def update_row_data(self, name_table:str, name_col:str, name_id:str, table_id:int, new_data):
        self.cursor.execute(f"""UPDATE {name_table} SET {name_col} = '{new_data}' WHERE {name_id} = '{table_id}';""")
        self.connect.commit()

    def update_row_journals(self, journal_id, new_name_journal, description):
        self.cursor.execute(f"""UPDATE Journals SET name_journal = '{new_name_journal}', description = '{description}' WHERE journal_id = '{journal_id}';""")
        self.connect.commit()

    def update_row_config(self, journal_id, config):
        self.cursor.execute(f"""UPDATE ConfigJournals SET config = '{config}' WHERE journal_id = '{journal_id}';""")
        self.connect.commit()

    def update_row_user(self, user_id, journal_id, data):
        self.cursor.execute(f"""UPDATE Users SET fname = '{data[0]}', lname = '{data[1]}', faname = '{data[2]}', weight = '{data[3]}', height = '{data[4]}', age = '{data[5]}', phone = '{data[6]}', birthday = '{data[7]}', gender = '{data[8]}' WHERE user_id = '{user_id}' AND journal_id = '{journal_id}';""")
        self.connect.commit()

    def update_row_data(self, user_id:str, journal_id:int, new_data):
        self.cursor.execute(f"""UPDATE Data SET  session_log = '{new_data}' WHERE journal_id = '{journal_id}' AND user_id = '{user_id}';""")
        self.connect.commit()

    def update_row_events(self, event_id, journal_id, new_data):
        self.cursor.execute(f"""UPDATE EventsJournals SET  date = '{new_data}' WHERE journal_id = '{journal_id}' AND event_id = '{event_id}';""")
        self.connect.commit()

    def get_last_id(self, name_col_id:str, name_table:str):
        id = self.cursor.execute(f"SELECT {name_col_id} FROM {name_table}").fetchall() or 0
        if id != 0: id = id[-1][0]
        return id

    def get_last_task_id(self):
        id = self.cursor.execute(f"SELECT task_id FROM TaskEvent").fetchall() or 0
        if id != 0: id = id[-1][0]
        return id

    def get_journal_id(self, name_journal=None, name_table="Journals"):
        if name_journal:
            return self.cursor.execute(f"SELECT journal_id FROM {name_table} WHERE name_journal = '{name_journal}'").fetchone()[0]
        else:
            return 1

    def get_config_id(self, journal_id, name_journal=None, name_table="ConfigJournals"):
        if name_journal:
            return self.cursor.execute(f"SELECT journal_id FROM {name_table} WHERE journal_id = '{journal_id}'").fetchone()[0]
        else:
            return 1

    def get_session_log(self, user_id, journal_id, name_table="Data") -> dict:
        session_log = self.cursor.execute(f"""SELECT session_log FROM {name_table} WHERE user_id = '{user_id}' AND journal_id = '{journal_id}';""").fetchone() or None
        if session_log != None:
            session_log = json.loads(session_log[0])
        else:
            session_log = dict()
        return session_log
    
    def get_config_journal(self, journal_id, name_table="ConfigJournals"):
        config = self.cursor.execute(f"SELECT * FROM {name_table} WHERE journal_id = '{journal_id}'").fetchone()
        return json.loads(config[2])

    def get_data_user(self, user_id, journal_id, name_table="Users") -> tuple:
        return self.cursor.execute(f"SELECT * FROM {name_table} WHERE user_id = '{user_id}' AND journal_id = '{journal_id}'").fetchone()

    def get_events_journal(self, journal_id):
        return self.cursor.execute(f"SELECT * FROM EventsJournals WHERE journal_id = '{journal_id}'").fetchone()

    def get_all(self, name_table:str) -> tuple:
        return self.cursor.execute(f"SELECT * FROM {name_table}").fetchall()
    
    def get_all_by_id(self, name_col:str, id:str, name_table:str) -> tuple:
        return self.cursor.execute(f"SELECT * FROM {name_table} WHERE {name_col} = '{id}'").fetchall()
    
    def search_journal(self, journal_id, name_journal, name_table = "Journals"):
        journal = self.cursor.execute(f"SELECT journal_id FROM {name_table} WHERE journal_id = '{journal_id}' AND name_journal = '{name_journal}'").fetchone()
        if journal == None:
            return False
        return True
    
    def search_config(self, journal_id):
        config = self.cursor.execute(f"SELECT config_id FROM ConfigJournals WHERE journal_id = '{journal_id}'").fetchone()
        
        if config == None:
            return False
        return True
    
    def get_all_by_id_sorted(self, name_col:str, id:str, name_table:str) -> tuple:
        return self.cursor.execute(f"SELECT * FROM {name_table} WHERE {name_col} = '{id}' ORDER BY lname DESC ").fetchall()
