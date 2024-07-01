import discord
from discord.ext import commands
import os 
import datetime 
import requests
import re
import aiohttp

client = commands.Bot(command_prefix='', self_bot = True)
print("https://github.com/pinkiwinter\n")


#1
def login_selection():
    print("Choose your login method:")
    print("1. Login with email and password")
    print("2. Login using a Discord account token")

    while True:
        choice = input("[!] Enter the number of your chosen option.\n> ")

        if choice == "1":
            oauth2_login()
            break
        elif choice == "2":
            token_login
            break
        else:
            print("\n[-] Invalid choice. Please try again.")


def token_login():
    global token
    while True:
        try:
            token = input("Enter your Discord account token.\n> ").strip()
            if not validate_token(token):  
                raise ValueError
        except ValueError as e:
            print("[-] Invalid token")
        else:
            print("[+] Token accepted.")
            break  


def oauth2_login():
        global token
        print("You have chosen to log in with email and password.")
        while True:
            email = input("Enter Email: ").strip()
            password = input("Enter Password: ").strip()

            payload = {
                "login": email,
                "password": password
            }
            headers = {
                "Content-Type": "application/json"
            }
            response = requests.post("https://discord.com/api/v9/auth/login", json=payload, headers=headers)
            if response.ok:
                print("> Data load... <")
                data = response.json()
                if 'token' in data:
                    token = data['token']
                    return token
                elif 'ticket' in data:
                    while True:
                        print("\nTwo-factor authentication is enabled. Please provide the code.")
                        code = input("Enter the authentication code: ").replace(" ", "")
                        token_payload = {
                            "code": code,
                            "ticket": data["ticket"]
                        }
                        token_response = requests.post("https://discord.com/api/v9/auth/mfa/totp", json=token_payload, headers=headers)
                        if token_response.ok:
                            token_data = token_response.json()
                            if 'token' in token_data:
                                token = token_data['token']
                                return token
                            else:
                                print("\n[-] Failed to retrieve token after 2FA authentication.")
                        else:
                            print("\n[-] Failed to authenticate using the provided code.")
                else:
                    print("\n[-] Unknown response format.")

            else:
                print("\n[-] Login Failed. Please check your credentials.")
        

            


def validate_token(token):
    pattern = r"^[\w-]+\.[\w-]+\.[\w-]+$"

    if re.fullmatch(pattern, token):
        return True
    else:
        return False
    

#2
selected_guilds_list = []
async def select_guilds():
    user_guild_list = []
    for index, guild in enumerate(client.guilds, start=1):
        print(f"{index}. {guild.name}")
        user_guild_list.append(guild)
    
    text = """↑
Here is the list of all the servers you are joined to, along with their corresponding numbers.
Please enter the number corresponding to the server you want to select. (if all --> 1000) ↓
Example: 12 8 22 9
> """

    selected_indicies = list(map(int, input(text).split()))

    for i in selected_indicies:
        if i != 1000:
            if 1 <= i <= len(user_guild_list):
                selected_guilds_list.append(user_guild_list[i - 1])
        else:
            selected_guilds_list.append(user_guild_list)


selected_dms_list = []
async def select_DMs():
    user_dms_list = []
    for index, dm in enumerate(client.private_channels, start=1):
        if isinstance(dm, discord.DMChannel):
            print(f"{index}. {dm.recipient.name}")
        else:
            sanitized_name = generate_group_name_if_none(dm)
            print(f"{index}. {sanitized_name}           <-- group")
        user_dms_list.append(dm)

    text = """
Now, please enter the number or username corresponding to the friend you want to select. (if all --> 1000) ↓
Example: 12 1 9 myflower 2 discorduser
> """
    selected_indicies = input(text).split()

    for i in selected_indicies:
        if i.isdigit():
            index = int(i)
            if 1 <= index <= len(user_dms_list):
                selected_dms_list.append(user_dms_list[index - 1])
            elif index == 1000:
                selected_dms_list.extend(user_dms_list)
        else:
            for o in user_dms_list:
                if isinstance(o, discord.DMChannel):
                    if o.recipient.name == i:
                        selected_dms_list.append(o)


#3
def ifexists(file):
    if os.path.exists(file):
        suffix = 1
        while os.path.exists(f"{file}_{suffix}"):
            suffix += 1
        file += f"_{suffix}"
    os.makedirs(file)
    return file


#4
invalid_char = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']   
def sanitize_name(name):                                                     
    for char in invalid_char:
        if char in name:
            name = name.replace(char, '-')

    return name


def generate_group_name_if_none(dm):
    members = [recipient.name for recipient in dm.recipients]
    members.append(client.user.name)

    dm.name = ', '.join(members)

    return dm.name


#5
async def main_folder():
    global main_folder_path
    main_folder_path = os.path.join(os.path.expanduser('~'), 'Documents', client.user.name)
    print(f"Creating main folder for: {client.user.name}...")
    print(f"> {main_folder_path} <")
    os.makedirs(main_folder_path)

    with open(os.path.join(main_folder_path, f"{client.user.name}.txt"), 'w', encoding="utf-8") as file:
        file.write(f"Display name: {client.user.display_name}\n")
        file.write(f"Username: {client.user.name}\n")
        file.write(f"Account creation data: {client.user.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"Total number of guilds: {len(client.guilds)}\n")
        file.write(f"Total number of friends: {len(client.user.friends)}\n")
    await icon(client.user, main_folder_path)

        
#6
async def messages_log(path, channel):
    with open(os.path.join(path, f"messages.txt"), 'w', encoding="utf-8") as file:
        try:
            async for message in channel.history(limit=None, oldest_first=True):
                file.write(f"{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write(f"{message.author.name}\n")
                
                if message.attachments:
                    for attachment in message.attachments:
                        file.write(f"> {attachment.url}\n")
                else:
                    file.write(f"> {message.content}\n")
                
                file.write('\n')
        except:
            pass


#7
async def icon(obj, path):
    if isinstance(obj, discord.DMChannel):
        url = obj.recipient.avatar_url
        name = obj.recipient.name
    elif isinstance(obj, discord.ClientUser):
        url = obj.avatar_url
        name = obj.name
    else:
        url = obj.icon_url
        name = obj.name

    if url:
        async with aiohttp.ClientSession() as session:
            async with session.get(str(url)) as response:
                if response.status == 200:
                    file_path = os.path.join(path, f"{name}.png")
                    with open(file_path, 'wb') as f:
                        f.write(await response.read())


#8
async def guild_structure_file(path):
    print(f"Creating guild_info.txt for guild: {guild.name}...")
    with open(os.path.join(path, f"guild_info.txt"), 'w', encoding="utf-8") as file:
        file.write(f"{guild.name}\n")
        for channel in guild.channels:
            if isinstance(channel, discord.CategoryChannel):
                file.write(f"- {channel.name}           <-- category\n")
                for text_channel in channel.text_channels:
                    file.write(f"- - {text_channel.name}            <-- chat\n")
                for voice_channel in channel.voice_channels:
                    file.write(f"- - {voice_channel.name}           <-- voice\n")
            elif isinstance(channel, discord.TextChannel):
                file.write(f"- - {channel.name}            <-- chat\n")
            elif isinstance(channel, discord.TextChannel):
                file.write(f"- - {channel.name}             <-- voice\n")
        file.write(f"\n\nMembers:\n")
        for member in guild.members:
            file.write(f"- {member.name}\n")
        file.write("\n\nRoles:\n")
        for role in guild.roles:
            file.write(f"- {role.name}\n")


async def all_dms_structure_file(path):
    print(f"Creating {client.user.name}'s DM's.txt...")
    with open(os.path.join(path, f"{client.user.name}'s DMs.txt"), 'w', encoding="utf-8") as file:
        file.write(f"{client.user.name}'s DMs\n")
        for obj in client.private_channels:
            if isinstance(obj, discord.DMChannel):
                file.write(f"- {obj.recipient.name}\n")
            else:
                file.write(f"- {obj.name}           <-- group\n")


#9
async def create_guild_directories(main_folder):
    global guild
    folder = os.path.join(main_folder, "Guilds")
    for guild in selected_guilds_list:
        guild.name = sanitize_name(guild.name)
        print(f"Creating folder for guild: {guild.name}...")
        guild_folders = os.path.join(folder, guild.name)
        ifexists(guild_folders)
        print(f"Creating structure file for guild: {guild.name}...")
        await guild_structure_file(guild_folders)
        print(f"Creating icon.png for group: {guild.name}...")
        await icon(guild, guild_folders)
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                print(f"Creating folder for channel: {channel.name}...")
                channel_folders = os.path.join(guild_folders, channel.name)
                channel_folders = ifexists(channel_folders)
                print(f"Creating messages.txt for channel: {channel.name}...")
                await messages_log(channel_folders, channel)


async def create_dms_directories(main_folder):
    dms_folder = os.path.join(main_folder, "DMs")
    dms_friends_folder = os.path.join(dms_folder, "friends")
    dms_groups_folder = os.path.join(dms_folder, "groups")
    for obj in selected_dms_list:
        if isinstance(obj, discord.DMChannel):
            print(f"Creating folder for friend: {obj.recipient.name}...")
            friend_folder = os.path.join(dms_friends_folder, obj.recipient.name)
            ifexists(friend_folder)
            print(f"Creating messages.txt for friend: {obj.recipient.name}...")
            await messages_log(friend_folder, obj)
            print(f"Creating icon.png for friend: {obj.recipient.name}...")
            await icon(obj, friend_folder)
        elif isinstance(obj, discord.GroupChannel):
            print(f"Creating folder for group: {obj.name}...")
            group_folder = os.path.join(dms_groups_folder, str(obj.name))
            ifexists(group_folder)
            print(f"Creating messages.txt for group: {obj.name}...")
            await messages_log(group_folder, obj)
            print(f"Creating icon.png for group: {obj.name}...")
            await icon(obj, group_folder)
            with open(os.path.join(group_folder, f"group_members.txt"), 'w', encoding='utf-8') as file:
                members = [recipient.name for recipient in obj.recipients]
                file.write("Members:\n")
                file.write(client.user.name + "\n")
                file.write("\n".join(members) + "\n")


login_selection()
@client.event
async def on_ready():
        print(f"Welcome! {client.user.name}.")

        await select_guilds()
        await select_DMs()
        await main_folder() 
        await create_guild_directories(main_folder_path)
        await create_dms_directories(main_folder_path)

        print("\n> Script executed successfully. <")


client.run(token)
