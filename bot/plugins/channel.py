import random
import string
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, FloodWait

from bot import VERIFY # pylint: disable=import-error
from bot.bot import Bot # pylint: disable=import-error
from bot.database import Database # pylint: disable=import-error
from bot.plugins.auto_filter import recacher # pylint: disable=import-error

db = Database()

@Client.on_message(filters.command(["add"]) & filters.group, group=1)
async def connect(bot: Bot, update):
    """
    A Funtion To Handle Incoming /add Command TO Connect A Chat With Group
    """
    chat_id = update.chat.id
    user_id = update.from_user.id if update.from_user else None
    target_chat = update.text.split(None, 1)
    global VERIFY
    
    if VERIFY.get(str(chat_id)) == None: # Make Admin's ID List
        admin_list = []
        async for x in bot.iter_chat_members(chat_id=chat_id, filter="administrators"):
            admin_id = x.user.id 
            admin_list.append(admin_id)
        admin_list.append(None)
        VERIFY[str(chat_id)] = admin_list

    if not user_id in VERIFY.get(str(chat_id)):
        return
    
    try:
        if target_chat[1].startswith("@"):
            if len(target_chat[1]) < 5:
                await update.reply_text("මොකේ Username එකක්ද බන් ඒ⁉...එහෙම එකක් නෑ බන්‼")
                return
            target = target_chat[1]
            
        elif not target_chat[1].startswith("@"):
            if len(target_chat[1]) < 14:
                await update.reply_text("ඒක Chat Id එකක්ද???\nවැරදියි බන්🙄.මෙහෙම එකක් එන්න ඕන :: <code>-100xxxxxxxxxx</code>")
                return
            target = int(target_chat[1])
                
    except Exception:
        await update.reply_text("Command එකේ වැරද්දක් තියනවා🧐\nබලහන් ඒක මේ වගේද කියල🙄 :: <code>/command -100xxxxxxxxxx)</code> or <code>/command @username</code>")
        return
    
    try:
        join_link = await bot.export_chat_invite_link(target)
    except Exception as e:
        print(e)
        await update.reply_text(f"<code>{target}</code> එකේ මං '<i>Inviting Users via Link</i>' Permission තියන Admin කෙනෙක්ද බලන්න...😐⁉නැත්තම් Admin දාල Permission දෙන්න‼")
        return
    
    userbot_info = await bot.USER.get_me()
    userbot_id = userbot_info.id
    userbot_name = userbot_info.first_name
    
    try:
        await bot.USER.join_chat(join_link)
        
    except UserAlreadyParticipant:
        pass
    
    except Exception:
        await update.reply_text(f"මට [{userbot_name}](tg://user?id={userbot_id}) එකට Connect වෙන්න බෑනෙ බං😥..`{target}` එකෙන් මාව Ban කරල තීයනවද බලන්න..Ban කරලනම් ආපහු Add කරන්න😭!!")
        return
    
    try:
        c_chat = await bot.get_chat(target)
        channel_id = c_chat.id
        channel_name = c_chat.title
        
    except Exception as e:
        await update.reply_text("මොකක්ද මගුලක් උනා😳...Log බලහන්‼")
        raise e
        
        
    in_db = await db.in_db(chat_id, channel_id)
    
    if in_db:
        await update.reply_text("මේක Add කරල බන් තියෙන්නෙ😬...‼")
        return
    
    wait_msg = await update.reply_text("වඩේ එලටම වෙනවා😋..\n<i>Files ටික DB එකට Add වෙන්න ටිකක් වෙලා යනවා‼</i>\nඑතකන් Commands දාන් නැතුව ඉවසලා ඉදාන්🙃..")
    
    try:
        type_list = ["video", "audio", "document"]
        data = []
        skipCT = 0
        
        for typ in type_list:

            async for msgs in bot.USER.search_messages(channel_id,filter=typ): #Thanks To @PrgOfficial For Suggesting
                
                # Using 'if elif' instead of 'or' to determine 'file_type'
                # Better Way? Make A PR
                try:
                    if msgs.video:
                        try:
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except FloodWait as e:
                            asyncio.sleep(e.x)
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except Exception as e:
                            print(e)
                            continue
                        file_id = file_id.video.file_id
                        file_name = msgs.video.file_name[0:-4]
                        file_caption  = msgs.caption if msgs.caption else ""
                        file_type = "video"
                    
                    elif msgs.audio:
                        try:
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except FloodWait as e:
                            asyncio.sleep(e.x)
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except Exception as e:
                            print(e)
                            continue
                        file_id = file_id.audio.file_id
                        file_name = msgs.audio.file_name[0:-4]
                        file_caption  = msgs.caption if msgs.caption else ""
                        file_type = "audio"
                    
                    elif msgs.document:
                        try:
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except FloodWait as e:
                            asyncio.sleep(e.x)
                            file_id = await bot.get_messages(channel_id, message_ids=msgs.message_id)
                        except Exception as e:
                            print(str(e))
                            continue
                        file_id = file_id.document.file_id
                        file_name = msgs.document.file_name[0:-4]
                        file_caption  = msgs.caption if msgs.caption else ""
                        file_type = "document"
                    
                    for i in ["_", "|", "-", "."]: # Work Around
                        try:
                            file_name = file_name.replace(i, " ")
                        except Exception:
                            pass
                    
                    file_link = msgs.link
                    group_id = chat_id
                    unique_id = ''.join(
                        random.choice(
                            string.ascii_lowercase + 
                            string.ascii_uppercase + 
                            string.digits
                        ) for _ in range(15)
                    )
                    
                    dicted = dict(
                        file_id=file_id, # Done
                        unique_id=unique_id,
                        file_name=file_name,
                        file_caption=file_caption,
                        file_type=file_type,
                        file_link=file_link,
                        chat_id=channel_id,
                        group_id=group_id,
                    )
                    
                    data.append(dicted)
                except Exception as e:
                    if 'NoneType' in str(e): # For Some Unknown Reason Some File Names are NoneType
                        skipCT +=1
                        continue
                    print(e)

        print(f"{skipCT} සමහර Files වල Name එක None උන හින්දා Skip කරා.#TG එකට බැනහන් ඒකට")
    except Exception as e:
        await wait_msg.edit_text("අව්ලක් කොල්ලො🤔..Log බලහන් පොඩ්ඩක්....")
        raise e
    
    await db.add_filters(data)
    await db.add_chat(chat_id, channel_id, channel_name)
    await recacher(chat_id, True, True, bot, update)
    
    await wait_msg.edit_text(f"DB එකට Add කරල ඉවරයි😁..ඔක්කොම Files <code>{len(data)}</code> තිබ්බා😍😋")


@Client.on_message(filters.command(["del"]) & filters.group, group=1)
async def disconnect(bot: Bot, update):
    """
    A Funtion To Handle Incoming /del Command TO Disconnect A Chat With A Group
    """
    chat_id = update.chat.id
    user_id = update.from_user.id if update.from_user else None
    target_chat = update.text.split(None, 1)
    global VERIFY
    
    if VERIFY.get(str(chat_id)) == None: # Make Admin's ID List
        admin_list = []
        async for x in bot.iter_chat_members(chat_id=chat_id, filter="administrators"):
            admin_id = x.user.id 
            admin_list.append(admin_id)
        admin_list.append(None)
        VERIFY[str(chat_id)] = admin_list

    if not user_id in VERIFY.get(str(chat_id)):
        return
    
    try:
        if target_chat[1].startswith("@"):
            if len(target_chat[1]) < 5:
                await update.reply_text("මොකේ Username එකක්ද බන් ඒ⁉...එහෙම එකක් නෑ බන්‼")
                return
            target = target_chat[1]
            
        elif not target_chat.startswith("@"):
            if len(target_chat[1]) < 14:
                await update.reply_text("ඒක Chat Id එකක්ද???\nවැරදියි බන්🙄.මෙහෙම එකක් එන්න ඕන :: <code>-100xxxxxxxxxx</code>")
                return
            target = int(target_chat[1])
                
    except Exception:
        await update.reply_text("Command එකේ වැරද්දක් තියනවා🧐\nබලහන් ඒක මේ වගේද කියල🙄 :: <code>/command -100xxxxxxxxxx)</code> or <code>/command @username</code>")
        return
    
    userbot = await bot.USER.get_me()
    userbot_name = userbot.first_name
    userbot_id = userbot.id
    
    try:
        channel_info = await bot.USER.get_chat(target)
        channel_id = channel_info.id
    except Exception:
        await update.reply_text(f"මට [{userbot_name}](tg://user?id={userbot_id}) එකේ Details හොයාගන්න බෑනෙ බං🧐..`{target}` එකෙන් මාව Ban කරල තීයනවද බලන්න..Ban කරලනම් ආපහු Add කරන්න😭!!")
        return
    
    in_db = await db.in_db(chat_id, channel_id)
    
    if not in_db:
        await update.reply_text("මහෙම මගුලකට මං Connect වෙලා නෑ බන්🤨...")
        return
    
    wait_msg = await update.reply_text("උබට ඕන විදියට වැඩේ වෙනවා😉...\nදැන් DB එකෙන් Files Delete වෙලා ඉවර වෙනකම් Commands එවල මේක කලවන් මැල්ලුමක් කරන් නැතුව ඉදහන්🤣")
    
    await db.del_filters(chat_id, channel_id)
    await db.del_active(chat_id, channel_id)
    await db.del_chat(chat_id, channel_id)
    await recacher(chat_id, True, True, bot, update)
    
    await wait_msg.edit_text("වැඩේ ඉවරයි🙂..\nFiles ටික DB එකෙන් Delete කරා😅.\nආපහු ADD කරන්න එහෙම කියකෝ🤬")


@Client.on_message(filters.command(["delall"]) & filters.group, group=1)
async def delall(bot: Bot, update):
    """
    A Funtion To Handle Incoming /delall Command TO Disconnect All Chats From A Group
    """
    chat_id=update.chat.id
    user_id = update.from_user.id if update.from_user else None
    global VERIFY
    
    if VERIFY.get(str(chat_id)) == None: # Make Admin's ID List
        admin_list = []
        async for x in bot.iter_chat_members(chat_id=chat_id, filter="administrators"):
            admin_id = x.user.id 
            admin_list.append(admin_id)
        admin_list.append(None)
        VERIFY[str(chat_id)] = admin_list

    if not user_id in VERIFY.get(str(chat_id)):
        return
    
    await db.delete_all(chat_id)
    await recacher(chat_id, True, True, bot, update)
    
    await update.reply_text("ඔක්කොම Connection ටික Delete කරා❌..\nDB එක හිස් දැන්...\nඔබට සතු‍ටුයිද දැන්???🤣🤣🤣🤣")


@Client.on_message(filters.channel & (filters.video | filters.audio | filters.document), group=0)
async def new_files(bot: Bot, update):
    """
    A Funtion To Handle Incoming New Files In A Channel ANd Add Them To Respective Channels..
    """
    channel_id = update.chat.id
    
    # Using 'if elif' instead of 'or' to determine 'file_type'
    # Better Way? Make A PR
    
    try:
        if update.video: 
            file_type = "video" 
            file_id = update.video.file_id
            file_name = update.video.file_name[0:-4]
            file_caption  = update.caption if update.caption else ""

        elif update.audio:
            file_type = "audio"
            file_id = update.audio.file_id
            file_name = update.audio.file_name[0:-4]
            file_caption  = update.caption if update.caption else ""

        elif update.document:
            file_type = "document"
            file_id = update.document.file_id
            file_name = update.document.file_name[0:-4]
            file_caption  = update.caption if update.caption else ""
        
        for i in ["_", "|", "-", "."]: # Work Around
            try:
                file_name = file_name.replace(i, " ")
            except Exception:
                pass
    except Exception as e:
        print(e)
        return
        
    
    file_link = update.link
    group_ids = await db.find_group_id(channel_id)
    unique_id = ''.join(
        random.choice(
            string.ascii_lowercase + 
            string.ascii_uppercase + 
            string.digits
        ) for _ in range(15)
    )
    
    data = []
    
    if group_ids:
        for group_id in group_ids:
            data_packets = dict(
                    file_id=file_id, # File Id For Future Updates Maybe...
                    unique_id=unique_id,
                    file_name=file_name,
                    file_caption=file_caption,
                    file_type=file_type,
                    file_link=file_link,
                    chat_id=channel_id,
                    group_id=group_id,
                )
            
            data.append(data_packets)
        await db.add_filters(data)
    return

