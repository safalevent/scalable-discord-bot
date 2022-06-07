# Scalable-Discord-PY-Bot
>This project is a discord bot with generic extension implementation and fundamental features. It uses Python and discord.py library.

## Features
- Has some fundamental functions and commands implemented, like _level system_ and a custom _help_ command.
- It is developed in a scalable context for more complex development cases.
- Default prefix is "**!**" and it can be changed and customized per server.
- Uses sqlite to save the data.
- Uses a custom wrapper for sqlite which you can see in the _data_ class.
- Loads every extension under the `/Extensions/` folder and has commands to unload and load them on runtime. Which helps developers develop more complex systems easily. To understand further about extensions, check [this documentation](https://discordpy.readthedocs.io/en/stable/ext/commands/extensions.html).
- Has utility functions and classes for some UI elements like buttons, select dropdowns, etc. **You should install discord.py version 2.0.0 which is beta and only available [on their github](https://github.com/Rapptz/discord.py) to use UI.**

## Requirements
- [Python](https://www.python.org/downloads/)
- [asqlite](https://github.com/Rapptz/asqlite)

## Installation
- __Using a python environment is recommended but not mandatory.__ [Click here to learn how to create and activate one.](https://docs.python.org/3/tutorial/venv.html)
- Install [asqlite](https://github.com/Rapptz/asqlite):
 `git clone https://github.com/Rapptz/asqlite.git`
 `pip install -U ./asqlite`
- _Not mandatory_. Install [discord.py 2.0 beta](https://github.com/Rapptz/discord.py):
 `git clone https://github.com/Rapptz/discord.py.git`
 `pip install -U ./discord.py[voice]`
- Install the pip requirements: `pip install -r pip_requirements.txt`
- **Get a bot _token_ if you haven't yet** from [discord developer portal](https://discord.com/developers/docs/intro). Create an [application](https://discord.com/developers/applications). Create a bot for that application and save the bots token.
- Create a file named token with no file extension. **File's full name should be as `token`.** Paste your bot's token in this file and save.
- Add your own **discord id** to the bot_owners list in `Constants.py` to enable owner commands for yourself. [You can get help about getting your discord id here.](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-)
- Run the bot: `python Bot.py`

## Developing your own features.
Using [extensions](https://discordpy.readthedocs.io/en/stable/ext/commands/extensions.html) are highly recommended to develop new features. You can use the already implemented non-functional extension called `ExampleExtension` to start. Learn more about the discord.py and how extensions work using [official discord.py documentation](https://discordpy.readthedocs.io/en/stable/). The bot loads all extensions under `/Extensions/` on start excluding the ones that start with a underscore(\_). Developer can use `extensions load` and `extensions unload` commands to load and unload extensions on runtime.

## 🤝 Contributing
1. [Fork the repository](https://github.com/safalevent/basic-discord-py-bot.git)
2. Clone your fork: `git clone https://github.com/safalevent/basic-discord-py-bot.git`
3. Create your feature branch: `git checkout -b my-new-feature`
4. Commit your changes: `git commit -am 'Add some feature'`
5. Push to the branch: `git push origin my-new-feature`
6. Submit a pull request
