import logging
import os

from discord.ext.commands.errors import NoEntryPointError

extension_folder = "Extensions"
extension_root_path = extension_folder.replace("/", ".") + "."

def get_all_extension_list():
    return [x for x in os.listdir("./" + extension_folder) if not x.startswith("_")]


def get_pure_extension_list(bot):
    extension_list = []
    for extension in bot.extensions:
        extension_list.append(extension.replace(extension_root_path, ""))

    return extension_list

def unload_loaded_extensions(bot):
    for extension in get_pure_extension_list(bot):
        _unload_extension(bot, extension_root_path + extension)

def load_all_extensions(bot):
    for extension in get_all_extension_list():
        _load_extension(bot, extension_root_path + extension)

def load_extension(bot, name):
    _load_extension(bot, extension_root_path + name)

def unload_extension(bot, name):
    _unload_extension(bot, extension_root_path + name)

def reload_extension(bot, name):
    _reload_extension(bot, extension_root_path + name)


def _load_extension(bot, extension):
    try:
        bot.load_extension(extension)
    except (NoEntryPointError) as e:
        logging.info(str(e))
        
def _unload_extension(bot, extension):
    try:
        bot.unload_extension(extension)
    except (NoEntryPointError) as e:
        logging.info(str(e))

def _reload_extension(bot, extension):
    try:
        bot.reload_extension(extension)
    except (NoEntryPointError) as e:
        logging.info(str(e))

