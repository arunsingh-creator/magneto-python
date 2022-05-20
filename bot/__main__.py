import os
import shutil, psutil
import signal
from sys import executable
import time
from telegram.ext import CommandHandler
from bot import bot, dispatcher, updater, botStartTime
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, delete
from pyrogram import idle
from bot import app


def stats(update, context):
    currentTime = get_readable_time(time() - botStartTime)
    osUptime = get_readable_time(time() - boot_time())
    total, used, free, disk= disk_usage('/')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(net_io_counters().bytes_sent)
    recv = get_readable_file_size(net_io_counters().bytes_recv)
    cpuUsage = cpu_percent(interval=0.5)
    p_core = cpu_count(logical=False)
    t_core = cpu_count(logical=True)
    swap = swap_memory()
    swap_p = swap.percent
    swap_t = get_readable_file_size(swap.total)
    memory = virtual_memory()
    mem_p = memory.percent
    mem_t = get_readable_file_size(memory.total)
    mem_a = get_readable_file_size(memory.available)
    mem_u = get_readable_file_size(memory.used)
    stats = f'<b>•• ━━ Red Club X Mirror Bot ━━ ••</b>\n\n'\
            f'<b>⏰Bot Uptime:</b> {currentTime}\n'\
            f'<b>☬OS Uptime:</b> {osUptime}\n\n'\
            f'<b>•• DISK INFO ••</b> \n'\
            f'<b>📁Total Disk Space:</b> {total}\n'\
            f'<b>☠Used:</b> {used} | <b>✨Free:</b> {free}\n\n'\
            f'<b>•• DATA USAGE ••</b> \n'\
            f'<b>📤Upload:</b> {sent}\n'\
            f'<b>📥Download:</b> {recv}\n\n'\
            f'<b>•• SERVER STATS ••</b> \n'\
            f'<b>🖥️CPU:</b> {cpuUsage}%\n'\
            f'<b>📦RAM:</b> {mem_p}%\n'\
            f'<b>📀DISK:</b> {disk}%\n\n'\
            f'<b>➤Physical Cores:</b> {p_core}\n'\
            f'<b>☞Total Cores:</b> {t_core}\n\n'\
            f'<b>✨SWAP:</b> {swap_t} | <b>🤗Used:</b> {swap_p}%\n'\
            f'<b>💿Memory Total:</b> {mem_t}\n'\
            f'<b>📀Memory Free:</b> {mem_a}\n'\
            f'<b>💿Memory Used:</b> {mem_u}\n'
    keyboard = [[InlineKeyboardButton("CLOSE", callback_data="stats_close")]]
    sendMessage(stats, context.bot, update)


def start(update, context):
    buttons = ButtonMaker()
    buttons.buildbutton("Main Channel", "https://t.me/redxclub")
    buttons.buildbutton("Mirror Group", "https://t.me/+GAXDf5pR4vk0ZmM1")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
    start_string = f'''
This is a bot only work in @redxclub mirror group join the group to use it
'''
    sendMessage(start_string, context.bot, update)


def restart(update, context):
    restart_message = sendMessage("Restarting, Please wait Till Then!", context.bot, update)
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


def bot_help(update, context):
    help_string = f'''
/{BotCommands.HelpCommand}: To get this message

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Start mirroring the link to google drive.\nPlzzz see this for full use of this command https://telegra.ph/Magneto-Python-Aria---Custom-Filename-Examples-01-20

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link] : starts mirroring and if downloaded file is any archive , extracts it to google drive

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: start mirroring and upload the archived (.tar) version of the download

/{BotCommands.WatchCommand} [youtube-dl supported link]: Mirror through youtube-dl. Click /{BotCommands.WatchCommand} for more help.

/{BotCommands.TarWatchCommand} [youtube-dl supported link]: Mirror through youtube-dl and tar before uploading

/{BotCommands.CancelMirror} : Reply to the message by which the download was initiated and that download will be cancelled

/{BotCommands.StatusCommand}: Shows a status of all the downloads

/{BotCommands.ListCommand} [search term]: Searches the search term in the Google drive, if found replies with the link

/{BotCommands.StatsCommand}: Show Stats of the machine the bot is hosted on

/{BotCommands.AuthorizeCommand}: Authorize a chat or a user to use the bot (Can only be invoked by owner of the bot)

/{BotCommands.LogCommand}: Get a log file of the bot. Handy for getting crash reports

'''
    sendMessage(help_string, context.bot, update)


def main():
    fs_utils.start_cleanup()
    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Restarted successfully Start F*cking the Bot!", chat_id, msg_id)
        os.remove(".restartmsg")

    start_handler = CommandHandler(BotCommands.StartCommand, start,
                                   filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling()
    LOGGER.info("Bot Started!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()
