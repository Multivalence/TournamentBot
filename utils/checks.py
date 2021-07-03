import os

async def is_command_channel(ctx):
    return ctx.channel.id == int(os.environ["COMMAND_CHANNEL"])


async def is_music_channel(ctx):
    return ctx.channel.id == int(os.environ["MUSIC_COMMAND_CHANNEL"])


async def is_register_channel(ctx):
    return ctx.channel.id == int(os.environ["REGISTER-CHANNEL"])