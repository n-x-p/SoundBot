from time import sleep

from config import bot_token, ffmpeg_exe_path, beacon_mp3
import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from datetime import datetime
from youtube_dl import YoutubeDL

bot = commands.Bot(command_prefix="%")
url_pattern = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
music_queue = {}
now_playing = {}


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


@bot.event
async def on_message(message):
    """Command Preprocessor"""
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    message_user = f"{message.author.name}#{message.author.discriminator}"
    print(f"{now} {message_user} in #{message.channel.name} -- {message.clean_content}")
    await bot.process_commands(message)


@bot.command(pass_context=True)
async def join(ctx):
    """Join voice channel that message author is in"""
    author = ctx.message.author
    if author.voice is None:
        await ctx.send("No voice channel specified")
    else:
        await author.voice.channel.connect()


@bot.command(pass_context=True)
async def disconnect(ctx):
    """
        Disconnects bot from voice channel
        - Can only be used while message author is
          in the same voice channel as bot
    """
    author = ctx.message.author
    if author.voice is None:
        await ctx.send("No voice channel specified")
    else:
        for x in bot.voice_clients:
            if x.channel == ctx.message.author.voice.channel:
                return await x.disconnect()


@bot.command(pass_context=True)
async def beacon(ctx):
    """Beacon audio test"""
    voice_channel = ctx.message.author.voice.channel
    if voice_channel is not None:
        vc = await voice_channel.connect()
        vc.play(discord.FFmpegPCMAudio(executable=ffmpeg_exe_path, source=beacon_mp3))
        # Sleep while audio is playing.
        while vc.is_playing():
            sleep(.1)
        await vc.disconnect()
    else:
        await ctx.send(str(ctx.author.name) + "is not in a channel.")


@bot.command(pass_context=True, brief="Plays a single video, from a youtube info_url")
async def play(ctx, url):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if ctx.guild not in music_queue.keys():
        music_queue[ctx.guild] = []

    queue_item = {
        'url': url
    }
    if not voice.is_playing():
        await ctx.send("playing...")
        music_queue[ctx.guild].append(queue_item)
        play_url(ctx, voice)
    else:
        await ctx.send("adding to queue...")
        music_queue[ctx.guild].append(queue_item)
        await ctx.send("added!")
        return


def play_url(ctx, voice):
    ydl_options = {
        'format': 'bestaudio',
        'noplaylist': 'True'
    }
    ffmpeg_options = {
        'executable': ffmpeg_exe_path,
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    while len(music_queue[ctx.guild]) > 0:
        now_playing[ctx.guild] = music_queue[ctx.guild][0]['url']
        music_queue[ctx.guild].pop(0)
        if voice.is_playing:
            sleep(1)
        try:
            with YoutubeDL(ydl_options) as ydl:
                info = ydl.extract_info(now_playing[ctx.guild], download=False)
            info_url = info['formats'][0]['url']
            audio_data = FFmpegPCMAudio(info_url, **ffmpeg_options)
            voice.play(audio_data)
            voice.is_playing()
        except RuntimeError:
            print("something went wrong. moving onto next song")


bot.run(bot_token)
