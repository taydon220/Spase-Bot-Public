import db_functions
import logging
import markov
import os
from random import randint, random

log = logging.getLogger(__name__)

triggers_and_responses = {"good bot": "Awwh! Thank you so much!", "bad bot": u"\U0001F920",
                          "git good": "git: 'good' is not a git command. See 'git --help'",
                          "git gud": "git: 'gud' is not a git command. See 'git --help'",
                          "git --help": "Pssh, help yourself. https://git-scm.com/docs/git"}


triggers_and_reactions = {220054802829148161: u"\U0001F920"}


trigger_words = triggers_and_responses.keys()


def __get_trigger_word(message_content):
    for trigger in trigger_words:
        if trigger.lower() in message_content.lower():
            return trigger
    return None


def __build_chance_response(message_content):
    words = message_content.split(" ")
    topic = words[randint(0, len(words) - 1)]
    response = markov.respond_db(topic)
    if response is not None:
        while len(response.split(" ")) < 3:
            log.info("Response too short. Adding another chain.")
            response = response.rstrip('.?!') + ', ' + markov.respond_db().lower()
    return response


def __chance_message_check(message_content):
    return random() < .05 and not message_content.startswith("$") and not message_content.startswith(";;")


def get_static_response(message_content):
    trigger_word = __get_trigger_word(message_content)
    return triggers_and_responses[trigger_word] if trigger_word is not None else None


def get_chance_response(message_content):
    return __build_chance_response(message_content) if __chance_message_check(message_content) else None


def get_reaction_response(author_id):
    return triggers_and_reactions[author_id] if author_id in triggers_and_reactions.keys() else None


def add_message_to_db(values):
    database = os.getenv("database")
    table_name = "all_messages"
    if not db_functions.table_exists(database, table_name):
        db_functions.create_table(database, table_name)
    db_functions.insert_into_table(database, table_name, values)


def add_chance_to_db(random_message_values):
    markov.add_response_to_db(random_message_values)
