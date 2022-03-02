# Basic-Discord-PY-Bot
>This project is a discord bot with generic extension implementation and fundamental features. It uses Python and discord.py library.

## Features
- Has some fundamental functions and commands implemented like _level system_ and a custom _help_ command.
- Default prefix is "**!**" and it can be changed and customized per server.
- Uses sqlite to save the data.
- Uses a custom wrapper for sqlite which you can see under the _Data_ class.
- Loads every extension under the `Extensions` folder and has commands to unload and load then on runtime. Which helps developers develop more complex systems easily. To understand further about extensions, check [this documentation](https://discordpy.readthedocs.io/en/stable/ext/commands/extensions.html).
- Has utility functions and classes for some UI elements like buttons, select dropdowns, etc. **You should install discord.py version 2.0.0 which is beta and only available [on their github](https://github.com/Rapptz/discord.py) to use UI.**

## Requirements
- [Python](https://www.python.org/downloads/)

## Installation
- __Creating a python environment is recommended but not mandatory.__ [Click here to learn how to create and activate one.](https://docs.python.org/3/tutorial/venv.html)
- Install the pip requirements: `pip install -r pip_requirements.txt`
- **Get a bot _token_ if you haven't yet** from [discord developer portal](https://discord.com/developers/docs/intro). Create an [application](https://discord.com/developers/applications). Create a bot for that application and save the bots token.
- Create an file named token with no extension. _File's name with extension should be as `token`._ Paste your bots token in this file and save.
- Run the bot: `python Bot.py`

## Developing your own features.
Using [extensions](https://discordpy.readthedocs.io/en/stable/ext/commands/extensions.html) are highly recommended to develop new features. You can use the already implemented no functional extension called `ExampleExtension` to start. And learn more about the discord.py using [official discord.py documentation](https://discordpy.readthedocs.io/en/stable/). The bot loads all extensions under `/Extensions/` on start excluding the ones that start with a underscore(\_). Developer can use `extensions load` and `extensions unload` commands to load and unload extensions on runtime.

## 🤝 Contributing
1. [Fork the repository](https://github.com/safalevent/basic-discord-py-bot.git)
2. Clone your fork: `git clone https://github.com/safalevent/basic-discord-py-bot.git`
3. Create your feature branch: `git checkout -b my-new-feature`
4. Commit your changes: `git commit -am 'Add some feature'`
5. Push to the branch: `git push origin my-new-feature`
6. Submit a pull request
