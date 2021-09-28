import db_functions
import os

DATABASE = os.getenv("database")


def get_quote_and_author_id():
    sql_statement = """SELECT content, author_id FROM all_messages WHERE (length(content) > 4)
                        AND NOT (content LIKE ';;%' OR content LIKE '$%')
                        AND author_id NOT IN ('184405311681986560','679006394107559947') ORDER BY RANDOM();"""
    results = db_functions.select_from_table(DATABASE, sql_statement)
    quote = results[0][0]
    author_id = results[0][1]
    return quote, author_id


def get_quote_from_id(author_id):
    sql_statement = """SELECT content FROM all_messages WHERE (author_id=?) AND (length(content) > 4)
                        AND NOT (content LIKE ';;%' OR content LIKE '$%')
                        AND author_id NOT IN ('184405311681986560','679006394107559947') ORDER BY RANDOM();"""
    results = db_functions.select_from_table(DATABASE, sql_statement, select_values=[author_id])
    return results[0][0]


if __name__ == "__main__":
    quote_and_author = get_quote_and_author_id()
    print(f"quote_and_author={quote_and_author}")  # list with 1 tuple
    print(f"quote_and_author[0]={quote_and_author[0]}")  # tuple
    print(f"quote_and_author[0][0]={quote_and_author[0][0]}")
    print(f"quote_and_author[0][1]={quote_and_author[0][1]}")