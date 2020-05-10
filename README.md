# Test bot that can use Google Dialogflow for response 
***
## Introduction
Application created for answering on a natural language questions. It exploits
the power of Google dialogFLow framework and social network [Vkontacte](vk.com)
and [Telegram](https://tlgrm.ru/) Messenger.      


## Local installation
For local installation use requirements:  
 `$pip install requirements.txt`  
Follow by this instruction [instructions: how-do-i-create-a-bot](https://core.telegram.org/bots/faq#how-do-i-create-a-bot).
Repeat it twice one Bot will serve for customers and the second one will send errors to you.
Get chat_id which equal to user Id from the special Bot _@userinfobot_.
Create project in the [GCP](https://cloud.google.com/dialogflow/docs/quick/setup)
Create Google service account and store `Google credential.json` locally
Create [VK](vk.com) account, public group and get VK_API token on page `https://vk.com/club<your_vk_id>?act=tokens`  
Create `.env` file with settings:
* TLG_TOKEN
* VK_API
* DF_PROJECT
* GOOGLE_APPLICATION_CREDENTIALS
* VK_GROUP
* SVC_TLG_TOKEN
* TLG_CHAT_ID
* HTTPS_PROXY (it is needed only to circumvent some country's restrictions)
   
## Google DialogFlow
Create DialogFlow [Agent](https://cloud.google.com/dialogflow/docs/quick/build-agent)
For the testing purpose it makes sense to get the set of questions and answers
 from [this place](https://dvmn.org/filer/canonical/1556745451/104/).
 To get this q&a set execute this: `python df_intents.py --intents_mode download`
 You'll get `question.json` in the project directory. To setup intent set into the agent run:  
`python df_intents.py --intents_mode upload`. It teaches your Agent to answer.
You can review is it well done via the browser.

## Local check how it works
Run this  `python tlg_bot.py` then go to chat with the Bot. Ask him the any phrase from `json-file`
with *question* key. He should answer from appropriate answer from the list of *answers* keys. 
Do the same with `vk_bot.py`.


## Deploying onto remote server (HEROKU)
### Registration (you can skip this step if you already have an account)
* [Sign up](https://signup.heroku.com/login) by this link.
* Fork this repo if you will
* create an app. You will need two one for *Telegram* and second for *VK*
* Link your repo with your applications
* It necessitates creating few settings, that described in the Local installation section, on the _Settings Tab_ of the app.
* There is another trick is needed for Google authentication. Create Buildpack on the Settings Tab from the https://github.com/psergal/heroku-google-application-credentials-buildpack
* Create another two *Config Vars* following the README.MD provided by this link. 
* Deploy applications
   
The [procfile](https://devcenter.heroku.com/articles/procfile) has one line for each app: 
* bot-tlg: python3 tlg_bot.py
* bot-vk: python3 vk_bot.py  
Switch on one bot for each app on the *Resources Tab*
  

## Project Goals
The code has been written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/modules/)

## License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/psergal/bitly/blob/master/license.md) file for details  

 

