<div markdown="1" align="center">    

![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)

</div>

<p align="center" markdown="1">

</p>

<p align="center">
  # Project Title
</p>

<p align="center">
A brief description of what this project does and who it's for
</p>

<p align="center">
[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)
</p>

## Demo

Wanna try breaking it?:
https://discord.gg/8GWc9xNjX8


## Deployment

To self-host this project:
1. Create a new application on https://discord.com/developers/applications.
2. Create a new bot in the application.
3. Add the bot to a server and get the bot's token and the server's target bot channel's id.
4. Create a free cluster on https://www.mongodb.com/ and get its log in link and password.
5. Create a database and three collections inside it. First one is for future reminders, second one is for past reminders, third one is for user profiles.
6. Create a project on https://replit.com and connect it with your fork of this repository (or manually copy the code there).
7. Create replit environment variables described in .env_sample_file and fill them with your values.
8. Run the code on replit and copy the link of the created website.
9. Create a new monitor on https://uptimerobot.com/ on the link of aforementioned website.
10. Done! The bot is ready to use. Contact me if you have any questions.

```bash
  npm run deploy
```


## Environment Variables

To run this project, you will need to add the following environment variables.

`DATABASE_NAME=MONGO_BOT_DATABASE_NAME`

`PAST_REMINDERS_COLLECTION_NAME=PAST_REMINDERS`

`FUTURE_REMINDERS_COLLECTION_NAME=FUTURE_REMINDERS`

`REMINDERBOT_USERS_PROFILES_COLLECTION_NAME=USERS_PROFILES`

`MONGODB_LINK=mongodb+srv://myusername:{}@myusername.bl5bla.mongodb.net/test`

`PW=TESTPW`

`TOKEN=as21d4f1vSWZXSzvErY12314LoNG4SW22adfdffa45afds512TokEn1sdaf2304fd`

`CHANNEL_ID=65735462653125342`

`LOCAL_TIMEZONE=US/Eastern`


## Features
- Reminders on a certain point in the future
- Reminders after some time interval from the present
- List view of 10 upcoming reminders of everyone
- List view of 10 upcoming reminders of yours
- Seeing the details of a reminder
- Deleting a reminder


## Support

For support, email fake@fake.com.


## Usage/Examples

<screens>


## Authors

- [@BSski](https://www.github.com/BSski)

