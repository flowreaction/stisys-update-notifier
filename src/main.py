"""
simple script to notify me when an update on the stisys exams page has occured. When a new grade
has been uploaded to stisys this script notifies me via telegram with the module and the grade
which i have received.

Author: Florian Bopp
Date: 2.2.2020
"""

import re
import json
import datetime
import requests
import credentials

CURRENT_TIME = datetime.datetime.now().strftime("%Y-%m-%d @ %H:%M:%S")

def get_html():
    """sends POST and GET request to stisys server
    to get the raw HTML of the results page

    Returns:
        String -- raw html string of the results page
    """
    post_login_url = 'https://stisys.haw-hamburg.de/login.do'
    request_url = 'https://stisys.haw-hamburg.de/viewExaminationData.do'
    payload = {
        'username': credentials.username,
        'password': credentials.password
    }
    with requests.Session() as session:
        session.post(post_login_url, data=payload)
        r = session.get(request_url)
        return ' '.join(r.text.split()) #r.text.replace('\n',' ')

def parse_html(raw_html):
    """Function to parse the html for the results information

    Arguments:
        raw_html {string} -- raw html string containing the entire results page

    Returns:
        list -- a list of the information from the results page in the format of
                [course_a, grade_a, course_b, grade_b, ..., course_n, grade_n]
    """
    parsed = re.findall("""((?<=<td></td> <td>).+?(?=&nbsp))|((?<="right">).+?(?=</td>))""", raw_html)
    formatted = []
    for x in parsed:
        for y in x:
            if y:
                formatted.append(y.strip())
            else:
                pass
    return formatted

def list_to_dict(lst):
    """converts the list of course-grade-pairs into a dictionary

    Arguments:
        lst {list} -- list in format of
                        [course_a, grade_a, course_b, grade_b, ..., course_n, grade_n]


    Returns:
        dict -- a dictionary in format of
                {course_a : grade_a, course_b : grade_b, ..., course_n : grade_n }
    """
    op = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return op

def compare_to_previous(new_data):
    """compares the current state of the courses and grades with the previous downloaded state,
        if change is detected, that change will be returned.
        This function overwrites the prevois data in the datafile.json after it has been compared
        to the current data.
        If no datafile.json exists, one will be created.

    Arguments:
        new_data {dict} -- a dictionary in format of
                            {course_a : grade_a, course_b : grade_b, ..., course_n : grade_n }

    Returns:
        dict -- returns a dict of the differences of the new and previous data in format of
                {course_a : grade_a, course_b : grade_b, ..., course_n : grade_n }
    """
    try:
        with open('./datafile.json', 'r') as file:
            json_string = file.read()
            old_data = json.loads(json_string)
            differences = {k : new_data[k] for k in set(new_data) - set(old_data)}

    except IOError:
        print(CURRENT_TIME + ' -> File not found')
        differences = None
    finally:
        with open('./datafile.json', 'w') as outfile:
            print(CURRENT_TIME + ' -> Writing new data to file')
            json_data = json.dumps(new_data)
            outfile.write(json_data)
            return differences

def telegram_bot_sendtext(bot_message):
    """Sends a formatted message to the telegram user with ID specified in credential.py

    Arguments:
        bot_message {string} -- the custom message to be send

    Returns:
        dict -- response object from telegram server
    """
    bot_token = credentials.bot_token
    bot_chat_id = credentials.bot_chatid
    send_text = 'https://api.telegram.org/bot' + bot_token + \
        '/sendMessage?chat_id=' + bot_chat_id + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    print(CURRENT_TIME + " -> Message sent through Telegram")
    return response.json()

def send_notification(diff):
    """if differences in the two versrions of the data were detected, a message with the
        differences in pretty format will be generated and passed to the telegram_bot_sendtext
        function.


    Arguments:
        diff {dict} -- dictionary of the differences
    """
    if diff:
        message = ''
        for k in diff:
            message += '- ' + str(k) + ': ' + diff[k] + '\n'
        telegram_bot_sendtext('Hi!\nThese new grade(s) have I just found: \n\n' + message)
        print(CURRENT_TIME + " -> " + str(diff))
    else:
        pass

if __name__ == "__main__":
    raw = get_html()
    PARSED_DATA = parse_html(raw)
    DATA_DICT = list_to_dict(PARSED_DATA)
    DIFFS = compare_to_previous(DATA_DICT)
    send_notification(DIFFS)
