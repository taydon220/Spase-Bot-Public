import db_functions
import os

# caller_author_id req
# channel_id req
# target_author_id optional
#
#


def message_counter(caller_author_id, channel_id, target_author_id=None):
    database = os.getenv("database")
    sql_statement = "SELECT count(*) FROM all_messages WHERE author_id=? AND channel_id=?"
    author_id = __build_author(caller_author_id, target_author_id)
    target_values = [author_id, channel_id]
    results = db_functions.select_from_table(database, sql_statement, select_values=target_values)
    return results[0][0]


# how can we use this function to split the validation + control?
def __build_author(caller_author_id, target_author_id):
    return target_author_id if target_author_id is not None else caller_author_id
