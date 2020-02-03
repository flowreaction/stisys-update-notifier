# stisys-update-notifier
This script, if used on a server with crontab, can check the stisys results page and return differences to the previous time it checked the page. If a change has happend it will send a message via a Telegram Bot to the desired chat-id (personal telegram id). 

To use this script yourself you will need to create a credentials.py file in the ./src/ dir next to the main.py file. Use the credentials_pattern.py as a template.

```python
username = 'Your HAW username(abc123)'
password = 'Your HAW password'
bot_token = 'your bot token from telegram'
bot_chatid = 'your pesonal chat id from telegram'
```

You will need to create your own Telegram-Bot.
To do so search for the BotFather on Telegram and type or press the /start command. The BotFather will explain the rest. Copy your API Token into the credentials.py 
Search for the Bot you just created in Telegram and add it by, again, typing /start.
Now got to ```https://api.telegram.org/bot<yourtoken>/getUpdates ``` replacing <yourtoken> with your actual token from the previous step.
You will get a json response object, search for the "id" keyword and copy the value to the credentials.py file.

If you have done these steps your bot should be able to send you messages.

I recommend running this script on a virtual server or a RaspberryPi with Crontab to automate the execution. If you have done so, you should be getting your update messages as soon as an update has appeared on the stisys results site.
