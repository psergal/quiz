# Quiz-bot that can play with you  
***
## Introduction
Application created for playing in a quiz. It has tons of questions to check your knowledge.
in the social network [Vkontacte](vk.com) and [Telegram](https://tlgrm.ru/) Messenger.      


## Local installation
For local installation use requirements:  
 `$pip install requirements.txt`

## Telegram installation notes
Follow by this instruction [instructions: how-do-i-create-a-bot](https://core.telegram.org/bots/faq#how-do-i-create-a-bot).
Repeat it twice one Bot will serve for customers and the second one will send errors to you.
You should have two telegram tokens
Get chat_id which equal to user Id from the special Bot _@userinfobot.
## VK installation notes
Create [VK](vk.com) account, public group and get VK_API token.
Follow instructions on page `https://vk.com/club<your_vk_id>?act=tokens`
Store somewhere API key, Group id  
## Redis
You will needed to save user activity in a key-value DB Redis.
Sign up [Redis Labs](https://redislabs.com/) and get the port number and the password for your database
## Environment setting  
Create `.env` file with list of settings:
* TLG_TOKEN
* VK_API
* REDIS_PASSWORD
* VK_GROUP
* SVC_TLG_TOKEN
* TLG_CHAT_ID
* REDIS_PORT
* HTTPS_PROXY (it is needed only to circumvent some country's restrictions)
   
## Local check how it works
Run this  `python TG_bot.py` then go to chat with your Bot. 
Start the quiz by launching `\start` command. Bot should show you Menu buttons.
Do the same with `VK_bot.py`. Chat with bot in a chat you've created before. 

## Deploying onto remote server (HEROKU)
### Registration (you can skip this step if you already have an account)
* [Sign up](https://signup.heroku.com/login) by this link.
* Fork this repo if you will
* create an app. You will need two one for *Telegram* and second for *VK*
* Link your repo with your applications
* It necessitates creating few settings, that described in the Local installation section, on the _Settings Tab_ of the app.
* Deploy applications
   
The [procfile](https://devcenter.heroku.com/articles/procfile) has one line for each app: 
* bot-tlg: python3 TG_bot.py
* bot-vk: python3 VK_bot.py  
Switch on one bot for each app on the *Resources Tab*
  

## Project Goals
The code has been written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/modules/)

## License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/psergal/bitly/blob/master/license.md) file for details  

