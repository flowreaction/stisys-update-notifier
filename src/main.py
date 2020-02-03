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

CURRENT_TIME = str(datetime.datetime.now())

def getHtml():
    postLoginUrl = 'https://stisys.haw-hamburg.de/login.do'
    requestUrl = 'https://stisys.haw-hamburg.de/viewExaminationData.do'
    payload = {
        'username': credentials.username,
        'password': credentials.password
    }
    with requests.Session() as session:
        session.post(postLoginUrl, data=payload)
        r = session.get(requestUrl)
        return ' '.join(r.text.split()) #r.text.replace('\n',' ')

def parseHtml(rawHtml):
    parsed = re.findall("""((?<=<td></td> <td>).+?(?=&nbsp))|((?<="right">).+?(?=</td>))""", rawHtml)
    formatted = []
    for x in parsed:
        for y in x:
            if y:
                formatted.append(y.strip())
            else:
                pass
    return formatted

def listToDict(lst):
    op = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return op

def compareToPrevious(newData):
    try:
        with open('./datafile.json', 'r') as file:
            jsonString = file.read()
            oldData = json.loads(jsonString)
            differences = {k : newData[k] for k in set(newData) - set(oldData)}

    except IOError:
        print(CURRENT_TIME + ' -> File not found')
        differences = None
    finally:
        with open('datafile.json', 'w') as outfile:
            print(CURRENT_TIME + ' -> Writing new data to file')
            jsonData = json.dumps(newData)
            outfile.write(jsonData)
            return differences

def telegram_bot_sendtext(bot_message):
    bot_token = credentials.bot_token
    bot_chatID = credentials.bot_chatid
    send_text = 'https://api.telegram.org/bot' + bot_token + \
        '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    print(CURRENT_TIME + " -> Message sent through Telegram")
    return response.json()

def sendNotification(diff):
    if diff:
        message = ''
        for k in diff:
            message += '- ' + str(k) + ': ' + diff[k] + '\n'
        telegram_bot_sendtext('Hi!\nThese new grade(s) have I just found: \n\n' + message)
        print(CURRENT_TIME + " -> " + str(diff))
    else:
        pass

if __name__ == "__main__":
    raw = getHtml()
    parsedData = parseHtml(raw)
    dataDict = listToDict(parsedData)
    diffs = compareToPrevious(dataDict)
    sendNotification(diffs)
