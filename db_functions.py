import logging
import sqlite3

log = logging.getLogger(__name__)


def table_exists(path_to_db, table_name):
    try:
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()
        cursor.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?""", (table_name,))
        if cursor.fetchone()[0] == 1:
            log.info("Table exists.")
            connection.commit()
            connection.close()
            return True
        else:
            log.info("No such table exists.")
            return False
    except sqlite3.Error as e:
        log.info(f"An error occurred: {e}")
        return False


def create_view(path_to_db):
    try:
        log.info("Creating the markov_acceptable view.")
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()
        cursor.execute("""CREATE VIEW IF NOT EXISTS markov_acceptable AS 
                                SELECT content FROM all_messages WHERE (length(content) > 1)
                                AND NOT (content LIKE ';;%' OR content LIKE '$%')
                                AND author_id NOT IN ('184405311681986560','679006394107559947');""")
        connection.commit()
        connection.close()
        log.info("View created if needed.")
    except sqlite3.Error as e:
        log.info(f"An error occurred: {e}")
    finally:
        try:
            if connection:
                connection.close()
                log.info("Connection closed.\n")
        except NameError:
            log.info("Connection closed.\n")


def create_table(path_to_db, table_name):
    try:
        connection = sqlite3.connect(path_to_db, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()
        log.info("Connected to SQLite.")
        log.info(f"Creating {table_name} if needed.")
        if table_name == "messages":
            cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
                            message_and_channel_id text PRIMARY KEY,
                            created_at timestamp NOT NULL,
                            message_id integer NOT NULL,
                            channel_id integer NOT NULL,
                            author_id integer NOT NULL,
                            author_display_name text,
                            content text NOT NULL
                            ) """)

        elif table_name == "markov_creations":
            cursor.execute("""CREATE TABLE IF NOT EXISTS markov_creations (
                            created_at timestamp NOT NULL,
                            message_id integer NOT NULL,
                            channel_id integer NOT NULL,
                            content text NOT NULL,
                            PRIMARY KEY (message_id, channel_id)
                            ) """)

        elif table_name == "all_messages":
            cursor.execute("""CREATE TABLE IF NOT EXISTS all_messages (
                            created_at timestamp NOT NULL,
                            message_id integer NOT NULL,
                            channel_id integer NOT NULL,
                            author_id integer NOT NULL,
                            author_display_name text,
                            content text NOT NULL,
                            PRIMARY KEY (message_id, channel_id)
                            ) """)

        elif table_name == "message_reactions":  # TODO implement usage in bot.
            cursor.execute("""CREATE TABLE IF NOT EXISTS message_reactions (
                            message_id integer NOT NULL,
                            channel_id integer NOT NULL,
                            emoji text NOT NULL,
                            content text NOT NULL,
                            PRIMARY KEY(message_id, channel_id)
                            ) """)
        connection.commit()
        connection.close()
    except sqlite3.Error as e:
        log.info("There was an error: ", e)
    finally:
        try:
            if connection:
                connection.close()
                log.info("Connection closed.\n")
        except NameError:
            log.info("Connection closed.\n")


def drop_table(path_to_db, table_name):
    try:
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()
        cursor.execute("DROP TABLE name=?", (table_name,))
        connection.commit()
        connection.close()
    except sqlite3.Error as e:
        log.info("An error occurred: {e}")
    finally:
        try:
            if connection:
                connection.close()
                log.info("Connection closed.\n")
        except NameError:
            log.info("Connection closed.\n")


def insert_into_table(path_to_db, table_name, insert_values):  # TODO build the dict from variables instead of strings
    try:
        sql_insert_templates = {"messages": """INSERT INTO messages (
                                                    message_and_channel_id, created_at, message_id, channel_id,
                                                    author_id, author_display_name, content)
                                                    VALUES(?,?,?,?,?,?,?)""",
                                "markov_creations": """INSERT INTO markov_creations (
                                                            created_at, message_id, channel_id, content)
                                                            VALUES(?,?,?,?)""",
                                "all_messages": """INSERT OR IGNORE INTO all_messages (
                                                        created_at, message_id, channel_id, author_id,
                                                        author_display_name, content)
                                                        VALUES(?,?,?,?,?,?)""",
                                "message_reactions": """INSERT INTO message_reactions (
                                                            message_id, channel_id, emoji, content)
                                                            VALUES(?,?,?,?)"""
                                }
        connection = sqlite3.connect(path_to_db, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()
        log.info("Connection to SQLite successful.")
        sql_statement = sql_insert_templates[table_name]
        if type(insert_values) == tuple:
            cursor.execute(sql_statement, insert_values)
        elif type(insert_values) == list:
            cursor.executemany(sql_statement, insert_values)
        connection.commit()
        connection.close()
        log.info(f"{table_name} table updated.")
    except sqlite3.Error as error:
        log.info("Failed to insert data to table", error)
    finally:
        try:
            if connection:
                connection.close()
                log.info("Connection closed.\n")
        except NameError:
            log.info("Connection closed.\n")


def select_from_table(path_to_db, sql_statement, select_values=None):
    try:
        connection = sqlite3.connect(path_to_db, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)  # detect_types will keep the datetime objects when inserted or selected.
        cursor = connection.cursor()
        if select_values is None:
            cursor.execute(sql_statement)
            records = cursor.fetchall()
            results = []
            for item in records:
                results.append(item)
        else:
            cursor.execute(sql_statement, select_values)
            records = cursor.fetchall()  # fetchall() returns a list of tuples.
            results = []
            for item in records:
                results.append(item)
        connection.commit()
        connection.close()
        log.info("Select complete; Connection closed.")
        return results
    except sqlite3.Error as error:
        log.info("Failed to read data from table.", error)
        return None
    finally:
        try:
            if connection:
                connection.close()
                log.info("Connection closed.\n")
        except NameError:
            log.info("Connection closed.\n")


def messages_to_sql_values(messages, table_name):
    """Converts a list of discord.Message objects to list of tuples of SQLite table values."""
    values = []
    for message in messages:
        if table_name == "messages":
            values.append((message.created_at, message.id, message.channel.id, message.author.id, message.author.display_name, message.content))
        elif table_name == "markov_creations":
            values.append((message.created_at, message.id, message.channel.id, message.content))
        elif table_name == "all_messages":
            values.append((message.created_at, message.id, message.channel.id, message.author.id, message.author.display_name, message.content))
    return values


def compare_last_db_to_last_message():
    pass