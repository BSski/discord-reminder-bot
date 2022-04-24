<div markdown="1" align="center">    

![App Screenshot](https://i.imgur.com/MgHd4jS.png)

</div>

<p align="center" markdown="1">

</p>

<p align="center">
  <h2 align="center">:hourglass: Discord Reminder Bot :date:</h2>
</p>

<p align="center">
A brief description of what this project does and who it's for
</p>


## :fireworks: Demo

Wanna test it or try breaking it? Join the test server: <br>
https://discord.gg/8GWc9xNjX8


## 🛠️ Deployment

To self-host this project for free:
1. Create a new application on https://discord.com/developers/applications.
2. Create a new bot in the application.
3. Add the bot to a server and get the bot's token and the server's target bot channel's ID.
4. Create a free cluster on https://www.mongodb.com/ and get its log in link and password. Customize the link to the format given below.
5. Create a database and three collections inside it. First one is for future reminders, second one is for past reminders, third one is for user profiles.
6. Create a project on https://replit.com and connect it with your fork of this repository (or manually copy the code there).
7. Create replit environment variables described below and fill them with your values.
8. Run the code on replit and copy the link of the created website.
9. Create a new monitor on https://uptimerobot.com/ on the link of aforementioned website. Keep the other parameters at default values.

🎇 Done! The bot is ready to use. 🎇

Feel free to contact me if you have any questions :slightly_smiling_face:


## :closed_lock_with_key: Environment Variables

To run this project, you will need to add the following environment variables (the values below are exemplary).

`DATABASE_NAME=MONGO_BOT_DATABASE_NAME`

`PAST_REMINDERS_COLLECTION_NAME=PAST_REMINDERS`

`FUTURE_REMINDERS_COLLECTION_NAME=FUTURE_REMINDERS`

`REMINDERBOT_USERS_PROFILES_COLLECTION_NAME=USERS_PROFILES`

`MONGODB_LINK=mongodb+srv://myusername:{}@myusername.bl5bla.mongodb.net/test`

`PW=TESTPW`

`TOKEN=as21d4f1vSWZXSzvErY12314LoNG4SW22adfdffa45afds512TokEn1sdaf2304fd`

`CHANNEL_ID=65735462653125342`

`LOCAL_TIMEZONE=US/Eastern`


## ❗ Commands

```
!remind me of X on 05.07.22 12:00
```
- Creates a reminder on a certain point in the future
```
!remind me of X in 15 mins
```
- Creates a reminder after some time interval from the present
```
!list_reminders
```
- Lists 10 upcoming reminders of everyone
```
!my_reminders
```
- Lists 10 upcoming reminders of yours
```
!show_reminder <ID>
```
- Shows the details of a reminder
```
!delete_reminder <ID>
```
- Deletes a reminder


## 🚀 Features
Besides commands behaviour, the bot also:
- validates user's profile (puts the user on a cooldown if needed),
- validates message content,
- validates date and time of a reminder.


## :sos: Support
<contact.bsski@gmail.com>


## 🧑🏻 Authors

- [@BSski](https://www.github.com/BSski)

