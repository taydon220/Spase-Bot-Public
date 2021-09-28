import logging
import numpy
import re
import db_functions
import os
from difflib import get_close_matches
from pprint import pformat

log = logging.getLogger(__name__)

DATABASE = os.getenv("database")


class MarkovResponse:
    def __init__(self, contents=[], topic=None, word_dict={}):
        self.contents = contents
        self.topic = topic
        self.word_dict = word_dict

    def __str__(self):
        return ' '.join(self.contents).capitalize().rstrip()

    def ready_to_send(self):  # Boolean return.
        if len(self.contents) > 1 and self.contents[-1].endswith('\n'):
            if self.contents[-2].endswith('.') or self.contents[-2].endswith('?') or self.contents[-2].endswith('!'):
                return True
            else:
                endings = ['.', '?', '!']
                self.contents[-2] = self.contents[-2] + numpy.random.choice(endings, p=[.7, .15, .15])
                self.contents.pop()
                return True
        else:
            return False

    def add_next_word(self):  # Returns True if successful, False if failure.
        error_count = 0
        result = False
        while not result:
            if error_count == 3:
                return result
            try:
                # log.info(f'Add next word attempt #{error_count+1}')
                self.contents.append(numpy.random.choice(self.word_dict[self.contents[-1]]))
                # if self.contents[-1] == '\n':
                    # log.info("Newline successfully added.")
                # else:
                    # log.info(f'{self.contents[-1]} successfully added.')
                # log.info(self.contents)
                result = True

            except KeyError:
                error_count += 1
                log.info(f'KeyError; Removing {self.contents[-1]} from end of chain.')
                self.contents = self.contents[:-1]
                return result
        return result


def add_response_to_db(random_message_values):
    database = DATABASE
    table_name = "markov_creations"
    if not db_functions.table_exists(database, table_name):
        db_functions.create_table(database, table_name)
    db_functions.insert_into_table(database, table_name, random_message_values)


def make_pairs(words):
    for i in range(len(words)-1):
        if words[i] == '\n':
            continue
        elif words[i].endswith('.') and words[i+1] == '\n':
            words[i].strip('.')
            yield (words[i], words[i+1])
        else:
            yield (words[i], words[i+1])


def create_word_dictionary_from_db(path_to_db):
    db_functions.create_view(path_to_db)
    sql_statement = "SELECT * FROM markov_acceptable"
    results = db_functions.select_from_table(path_to_db, sql_statement)
    results_with_newline = []
    all_words = []
    for content in results:
        results_with_newline.append(content[0] + '\n')
    for result in results_with_newline:
        match_list = re.findall(r'\S+|\n', result)
        for word in match_list:
            all_words.append(word)
    pairs = make_pairs(all_words)
    word_dict = {}
    for word1, word2 in pairs:
        if word1.lower() in word_dict.keys():
            word_dict[word1.rstrip('.,?!()*"').lstrip('.?!()*"').lower()].append(word2.rstrip('.,?!()*"').lstrip('.?!()*"').lower())
        else:
            word_dict[word1.rstrip('.,?!()*"').lstrip('.?!()*"').lower()] = [word2.rstrip('.,?!()*"').lstrip('.?!()*"').lower()]
    return word_dict  # Returns the dictionary and the all_words list


def log_word_dictionary(word_dict):
    with open('./logs/markov_dict.txt', 'w', encoding='utf8') as f:
        log.info(pformat(word_dict, f, indent=2))

    data = [word for word in word_dict.keys() if '.' not in word and '?' not in word]
    with open('./logs/potential_starts.txt', 'w', encoding='utf8') as f2:
        log.info(pformat(data, f2, indent=2))

    with open("./logs/messages.txt", encoding='utf8') as file:
        words = re.findall(r'\S+|\n', file.read())
    pairs = make_pairs(words)
    cleaned_pairs = []
    for word1, word2 in pairs:
        cleaned_pairs.append((word1.rstrip('".?!,(*').lstrip('.?!()*"').lower(), word2.rstrip('".?!,(*').lstrip('.?!()*"').lower()))
    with open('./logs/word_pairs.txt', 'w', encoding='utf8') as f3:
        for pair in cleaned_pairs:
            f3.write(str(pair) + "\n")


def find_similar_word(original, words):
    formatted_key_dict = {word.upper(): word for word in words}
    formatted_keys_list = [key for key in formatted_key_dict.keys()]
    # log.info(formatted_key_dict)
    # log.info(formatted_keys_list)
    close_matches = get_close_matches(original, formatted_keys_list, cutoff=.85)
    return formatted_key_dict[numpy.random.choice(close_matches)] if len(close_matches) > 0 else None
    # return numpy.random.choice(get_close_matches(original, words, cutoff=.85))


def console_menu():
    log.info('__________________________________________________\n')
    answer = input("Would you like to include a topic? y/n/quit: ")
    while answer.lower() not in ["y", "n", "quit", "test", "match"]:
        answer = console_menu()
    return answer


def respond_db(topic=None):  # TODO fix case sensitivity of topic being in potential starts.
    database = DATABASE
    word_dict = create_word_dictionary_from_db(database)
    potential_starts = [word for word in word_dict.keys() if '.' not in word and '?' not in word]

    if topic is not None and topic in potential_starts:
        contents = [topic]
        chain = MarkovResponse(contents=contents, topic=topic.lower(), word_dict=word_dict)
        log.info(f'On the topic of {chain.topic}...')
        while not chain.ready_to_send():
            if not chain.add_next_word():  # If fails to add words picks new start_word for chain.
                new_start = numpy.random.choice(potential_starts)
                log.info(f'New starting word = {new_start}')
                chain = MarkovResponse(contents=[new_start], topic=topic.lower(), word_dict=word_dict)
        return str(chain)
    elif topic is not None and topic not in potential_starts:
        try:
            new_topic = find_similar_word(topic, potential_starts)
            if new_topic is None:
                return None
            contents = [new_topic]
            chain = MarkovResponse(contents=contents, topic=new_topic.lower(), word_dict=word_dict)
            log.info(f'I think you meant to say: {chain.topic}...')
            while not chain.ready_to_send():
                if not chain.add_next_word():  # If fails to add words picks new start_word for chain.
                    new_start = numpy.random.choice(potential_starts)
                    log.info(f'New starting word = {new_start}')
                    chain = MarkovResponse(contents=[new_start], topic=topic.lower(), word_dict=word_dict)
            return str(chain)
        except ValueError:
            return None

    else:
        start_word = numpy.random.choice(potential_starts)
        # log.info(f'Original start_word = {start_word}')

        contents = [start_word]
        chain = MarkovResponse(contents=contents, topic=topic, word_dict=word_dict)

        while not chain.ready_to_send():
            if not chain.add_next_word():  # If fails to add words picks new start_word for chain.
                new_start = numpy.random.choice(potential_starts)
                log.info(f'New starting word = {new_start}')
                chain = MarkovResponse(contents=[new_start], topic=topic, word_dict=word_dict)
        return str(chain)


def get_past_creations(quantity):
    database = DATABASE
    sql_statement = """SELECT content from markov_creations order by RANDOM();"""
    return db_functions.select_from_table(database, sql_statement)[:quantity]


if __name__ == "__main__":
    while True:
        answer = console_menu()
        if answer.lower() == "y":
            topic = input("Enter a 1 word topic: ")
            response = respond_db(topic=topic.lower())
            while len(response.split(' ')) < 3:
                response = response.rstrip('.?!') + ', ' + respond_db().lower()
            log.info(response)
        elif answer.lower() == "n":
            sentences = []
            for x in range(10):
                response = respond_db()
                while len(response.split(' ')) < 3:
                    response = response.rstrip('.?!') + ', ' + respond_db().lower()
                sentences.append(response)
            log.info('__________________________________________________\n')
            for counter, sentence in enumerate(sentences, 1):
                log.info(counter, sentence)

        elif answer.lower() == "test":
            response = respond_db(topic=input("Topic? ").lower())
            while len(response.split(' ')) < 3:
                response = response.rstrip('.?!') + ', ' + respond_db().lower()
            log.info(response)
            sentences = []
            for x in range(10):
                response2 = respond_db()
                while len(response2.split(' ')) < 3:
                    response2 = response2.rstrip('.?!') + ', ' + respond_db().lower()
                sentences.append(response2)
            log.info('__________________________________________________\n')
            for counter, sentence in enumerate(sentences, 1):
                log.info(counter, sentence)

        elif answer.lower() == "match":
            test_word = input("Word? ")
            database = DATABASE
            word_dict = create_word_dictionary_from_db(database)
            potential_starts = [word for word in word_dict.keys() if '.' not in word and '?' not in word]
            case_dict = {key.lower() for key in word_dict.keys()}
            while not test_word == "quit":
                # log.info(get_close_matches(test_word, potential_starts, cutoff=.25))
                log.info(find_similar_word(test_word, potential_starts))
                test_word = input("Word? ")
        else:
            log_word_dictionary(create_word_dictionary_from_db(DATABASE))
            break
