import logging
import os

from discord.ext.commands.errors import NoEntryPointError

extension_folder_name = "Extensions"
extension_folder_path = "./" + extension_folder_name
extension_root_path = extension_folder_name.replace("/", ".") + "."

def get_all_extension_list():
    return [x for x in os.listdir(extension_folder_path) if not x.startswith("_")]

def get_pure_extension_list(bot):
    extension_list = []
    for extension in bot.extensions:
        extension_list.append(extension.replace(extension_root_path, ""))

    return extension_list

async def unload_loaded_extensions(bot):
    for extension in get_pure_extension_list(bot):
        await _unload_extension(bot, extension_root_path + extension)

async def load_all_extensions(bot):
    for extension in get_all_extension_list():
        await _load_extension(bot, extension_root_path + extension)

async def load_extension(bot, name):
    await _load_extension(bot, extension_root_path + name)

async def unload_extension(bot, name):
    await _unload_extension(bot, extension_root_path + name)

async def reload_extension(bot, name):
    await _reload_extension(bot, extension_root_path + name)


async def _load_extension(bot, extension):
    try:
        await bot.load_extension(extension)
    except (NoEntryPointError) as e:
        logging.info(str(e))
        
async def _unload_extension(bot, extension):
    try:
        await bot.unload_extension(extension)
    except (NoEntryPointError) as e:
        logging.info(str(e))

async def _reload_extension(bot, extension):
    try:
        await bot.reload_extension(extension)
    except (NoEntryPointError) as e:
        logging.info(str(e))