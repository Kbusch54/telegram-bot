from typing import Final
from telegram import Bot, Update,InlineKeyboardButton,InlineKeyboardMarkup
import requests
import threading
from web3 import Web3
import time
from supabase import create_client, Client
import os 
import json
import sys
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters,CallbackQueryHandler, CallbackContext,ConversationHandler
import asyncio

#Contract reading
sys.path.insert(1, '/main') 
with open("./position_router_abi.json") as f:
    info_json = json.load(f)
abi = info_json
dotenv_path = './.env'
load_dotenv(dotenv_path=dotenv_path)
infura_project_id:str = os.getenv('INFURA_API_KEY')
w3 = Web3(Web3.HTTPProvider(f'https://arb-mainnet.g.alchemy.com/v2/{infura_project_id}'))
GMXContractAddress = '0xb87a436B93fFE9D75c5cFA7bAcFff96430b09868' # GMX contract address
GMXContractABI = abi
GMXContract = w3.eth.contract(address=GMXContractAddress, abi=GMXContractABI)
index_tokens={'0x82aF49447D8a07e3bd95BD0d56f35241523fBab1':'Wrapped Ether (WETH)','0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f':'Wrapped BTC (WBTC)','0xf97f4df75117a78c1A5a0DBb814Af92458539FB4':'ChainLink Token (LINK)','0xFa7F8980b0f1E64A2062791cc3b0871572f1F7f0':'Uniswap (UNI)'}
def get_token(index_token):
    return index_tokens[index_token]
def get_side(isLong):
    if isLong:
        return 'Long'
    else:
        return 'Short'
def handle_event(event):
    sizeDelta = event['args']['sizeDelta'] / (10 ** 30)
    indexToken = event['args']['indexToken']
    account = event['args']['account']
    transactionHash = event['transactionHash']
    transactionHash = transactionHash.hex()
    base_link = "https://arbiscan.io/tx/"
    transaction_link = f'<a href="{base_link}{transactionHash}">TransactionHash</a>'
    if sizeDelta >= 100000:
        message_to_send =f'🐳 Whale Alert! 🐳\nToken: {get_token(indexToken)}\nPosition size:${round(sizeDelta,2)}USD\n{get_side(event["args"]["isLong"])}\nTrader: {account}\n\n {transaction_link}'
        loop = asyncio.get_event_loop()
        loop.run_until_complete(check_whales(message_to_send))


event_filter = GMXContract.events.ExecuteIncreasePosition.create_filter(fromBlock='latest')
def runnning_whale_check():
    while True:
        for event in event_filter.get_new_entries():

            handle_event(event)

TELEGRAM_TOKEN: Final= os.getenv("TELEGRAM_TOKEN")
BOT_USERNAME: Final = os.getenv("BOT_USERNAME")
  
dotenv_path = './.env'
load_dotenv(dotenv_path=dotenv_path)

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)



#Helper functions
def action_greater_message(action):
    if action == True:
        return 'greater than'
    else:
        return 'less than'
def get_token(index_token):
    return index_tokens[index_token]
def token_check(token):
    if token in TOKEN_OPTIONS:
        return True
    else:
        return False
async def check_change():
    for token, change in PRICE_CHANGES.items():
        if change in ['up']:
            await check_triggers(token,True,LAST_TOKEN_PRICE[token])
        if change in ['down']:
            await check_triggers(token,False,LAST_TOKEN_PRICE[token])
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
async def check_dailys():
    response = supabase.table("triggers").select("token, user_id,id").eq('type', 'daily').execute()
    if response.data == []:
        return
    triggers = response.data
    for trigger in triggers:
        await send_message(trigger['user_id'],f'Here is your daily reminder for {trigger["token"]}\n ${round(LAST_TOKEN_PRICE[trigger["token"]],2)}')
async def notify_user(user_id, token,price,new_price,actionType):
    typeOf = None
    if actionType == True:
        typeOf = 'greater than'
    else:
        typeOf = 'less than'
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=user_id, text=f'Alert!\nThe price of {token} is {typeOf} your trigger price of ${price}.\n Current Price is ${new_price}')

async def send_message(user_id, message):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')

async def send_message_reminder(user_id, message,keyboard):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=user_id, text=message, reply_markup=keyboard.to_dict())

#Database
#db push
def remove_trigger_from_db(trigger_id):
    try:
        supabase.table("triggers").delete().eq('id', trigger_id).execute()
    except Exception as e:
        print('error',e)
def add_trigger_daily(user_id, token:str):
    token_input = token
    trigger = {"token": token_input, "type": 'daily', "user_id": user_id,'created_at':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
    try:
        supabase.table("triggers").insert(trigger).execute()
    except Exception as e:
        print('error',e)
def db_triggered(trigger_id):
    trigger = {"has_reminded": True}
    try:
        supabase.table("triggers").update(trigger).eq('id', trigger_id).execute()
    except Exception as e:
        print('Triggered error',e)
def add_trigger_to_db(user_id, token, action, price):
    trigger = {"token": token, "type":'conditional','action_greater': action, "price": price, "user_id": user_id,'created_at':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'has_reminded': False}
    try:
        supabase.table("triggers").insert(trigger).execute()
    except Exception as e:
        print('error',e)
def remove_from_whale(user_id):
    try:
        supabase.table("users").update({"whale": False}).eq('user_chatid', user_id).execute()
    except Exception as e:
        print('error',e)
def add_user_to_db(user_id,whale=None):
    if whale == None:
        user = {"user_chatid": user_id}
    else:
        user = {"user_chatid": user_id, "whale": True}
    try:
        supabase.table("users").upsert(user).execute()
    except Exception as e:
        print('error',e)
#db pull
def get_all_whales():
    try:
        response = supabase.table("users").select("user_chatid").eq('whale',True).execute()
    except:
        print('error')
    if response.data == []:
        return
    whales = response.data
    return whales
async def get_untriggered_reminders(user_id):
    triggers = []
    messages = []
    try:
        response = supabase.table("triggers").select("id,token, type, price, action_greater,created_at").eq('user_id', user_id).neq('has_reminded', True).execute()
        triggers.extend(response.data)
    except:
        print('error')
    try:
        response2 = supabase.table("triggers").select("id,token, type, price, action_greater,created_at").eq('user_id', user_id).eq('type', 'daily').execute()
        triggers.extend(response2.data)
    except:
        print('error')
    try:
        response3 = supabase.table("users").select("whale").eq('user_chatid', user_id).execute()
        print(response3.data)
    except:
        print('error')

    if response3.data[0]['whale'] == True:
        whale_message = ('You are apart of the whale list. You will be notified when there are large movements in the market.')
        await send_message(user_id, whale_message)
    # Create inline keyboard
    for trigger in triggers:
        if trigger['type'] == 'daily':
            cancel_button = InlineKeyboardButton('Cancel', callback_data=f'cancel_{trigger["id"]}')
            keyboard = InlineKeyboardMarkup([[cancel_button]])
            message = ('Daily reminder for ' + trigger['token'] + ' created on ' + trigger['created_at'])
            messages.append((message, keyboard))
        if trigger['type'] == 'conditional':
            cancel_button = InlineKeyboardButton('Cancel', callback_data=f'cancel_{trigger["id"]}')
            keyboard = InlineKeyboardMarkup([[cancel_button]])
            message =('Conditional reminder for ' + trigger['token'] + ' created on ' + trigger['created_at'] + ' when price is ' + action_greater_message(trigger['action_greater']) + ' $' + str(trigger['price']))
            messages.append((message, keyboard))
    if messages != []:
        for message, keyboard in messages:
            response = await send_message_reminder(user_id, message, keyboard)
    else:
        await send_message(user_id, 'You have no reminders')
async def check_whales(message:str):
    accounts = get_all_whales()
    tasks = [send_message(account['user_chatid'], message) for account in accounts]
    await asyncio.gather(*tasks)
# Separate function to handle callback
async def handle_button_click(update, context):
    query = update.callback_query
    button_data = query.data
    if button_data.startswith('cancel_'):
        reminder_id = button_data[len('cancel_'):]
        text_message = query.message.text
        if reminder_id is not None:
            remove_trigger_from_db(reminder_id)
            # Handle the reminder cancellation
            edited_message = f"❌Deleted \n{text_message}\nDELETED❌"
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=edited_message
            )
            pass
async def check_triggers(token,action,new_price):
    token = token
    try:
        if action == True:
            response = supabase.table("triggers").select("price, user_id,id").eq('token', token).eq('action_greater', action).eq('has_reminded',False).lte('price', new_price).execute()
        else:
            response = supabase.table("triggers").select("price, user_id,id").eq('token', token).eq('action_greater', action).eq('has_reminded',False).gte('price', new_price).execute()
    except:
        print('error')
    if response.data == []:
        return
    triggers = response.data
    for trigger in triggers:
        await notify_user(trigger['user_id'], token, trigger['price'], new_price, action)
        db_triggered(trigger['id'])

#Global Variables
index_tokens={'0x82aF49447D8a07e3bd95BD0d56f35241523fBab1':'Wrapped Ether (WETH)','0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f':'Wrapped BTC (WBTC)','0xf97f4df75117a78c1A5a0DBb814Af92458539FB4':'ChainLink Token (LINK)','0xFa7F8980b0f1E64A2062791cc3b0871572f1F7f0':'Uniswap (UNI)'}
TOKEN_OPTIONS= ['Wrapped Ether (WETH)','Wrapped BTC (WBTC)','ChainLink Token (LINK)','Uniswap (UNI)']
LAST_TOKEN_PRICE = {}
PREV_TOKEN_PRICES = {}
PRICE_CHANGES = {}
current_token = None
trigger_type = None


#Getting Prices and Checking DB
async def do_reminders():
    while True:
        await fetch_token_prices()

        time.sleep(60*5)#5 minutes
async def do_daily_reminders():
    while True:
        time.sleep(60*60*24)#24 hours
        await check_dailys()
#Http requests
async def fetch_token_prices():
    response = requests.get('https://api.gmx.io/prices')
    tokens = response.json()
    token_prices = {}
    PREV_TOKEN_PRICES = LAST_TOKEN_PRICE.copy()
    LAST_TOKEN_PRICE.clear()
    PRICE_CHANGES.clear()
    token_prices = {get_token(address): int(price) / 10**30 for address, price in tokens.items()}
    for token_name, price in token_prices.items():
        LAST_TOKEN_PRICE[token_name] = price

        if token_name in PREV_TOKEN_PRICES:
            # If the price has increased, store 'up', otherwise store 'down'
            if price > PREV_TOKEN_PRICES[token_name]:
                PRICE_CHANGES[token_name] = 'up'
            elif price < PREV_TOKEN_PRICES[token_name]:
                PRICE_CHANGES[token_name] = 'down'
    await check_change()
    return token_prices


#Commands
async def start(update: Update,context):
    await update.message.reply_text("Hi! I'm a bot that will help you to keep track of your crypto portfolio. \n\n We track token prices on GMX \n\n To get started, type /new_reminder \n\n Type /tokens to get a list of tokens you can track \n\n Type /lastPrice to get the last price of all the tokens \n\n Type /reminders to get a list of your reminders \n\nType /whale_list to get added to the 🐳Whale alerts!\n\nType /remove_whale To stop whale alerts \n\nType /cancel anytime to end conversation")
async def help(update: Update,context):
    await update.message.reply_text("Hi! I'm a bot that will help you to keep track of your crypto portfolio. \n\n We track token prices on GMX \n\n To get started, type /new_reminder \n\n Type /tokens to get a list of tokens you can track \n\n Type /lastPrice to get the last price of all the tokens \n\nType /reminders to get a list of your reminders\n\nType /whale_list to get added to the 🐳Whale alerts!\n\nType /remove_whale To stop whale alerts \n\nType /cancel anytime to end conversation")
async def get_tokens(update: Update,context):
    await update.message.reply_text("Here are the list of tokens you have the option of tracking \n\n 1. Wrapped Ether (WETH)\n\n 2. Wrapped BTC (WBTC)\n\n 3. ChainLink Token (LINK)\n\n 4. Uniswap (UNI)") 
async def last_price(update: Update,context):
    token_prices_str = '\n'.join(f'{k}: {v}' for k, v in LAST_TOKEN_PRICE.items())
    await update.message.reply_text("Here are the lastet prices: \n\n" + token_prices_str)
    return ConversationHandler.END    
async def get_reminders(update: Update,context):
    await update.message.reply_text("Here are your reminders: \n\n") 
    await get_untriggered_reminders(update.message.chat_id)
    return ConversationHandler.END
async def remove_whale(update: Update,context):
    user_id = update.message.chat_id
    remove_from_whale(user_id)
    await update.message.reply_text("You have been removed from our whale list. You will no longer be notified when there are large movements in the market.")
    return ConversationHandler.END
#Entry Point
async def whale_sign_up(update: Update,context):
    user_id = update.message.chat_id
    add_user_to_db(user_id,True)
    await update.message.reply_text("You have been added to our whale list. You will be notified when there are large movements in the market.")
    return ConversationHandler.END
async def new_reminder(update: Update,context):
    user_id = update.message.chat_id
    add_user_to_db(user_id)
    await update.message.reply_text("Please choose your reminder \n\n 1. Daily \n\n 2. Conditional \n\n")
    return 1
#Conversations
async def cancel(update: Update, context: CallbackContext):
    print("cancel")
    await update.message.reply_text('Conversation cancelled.')
    ConversationHandler.END
    return 

async def new_reminder(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    add_user_to_db(user_id)
    await update.message.reply_text("Please choose your reminder \n\n 1. Daily \n\n 2. Conditional \n\n")
    return 1

async def token_select(update: Update, context: CallbackContext):
    global trigger_type
    trigger_type = update.message.text
    if trigger_type not in ['1', '2']:
        await update.message.reply_text("Please choose \n\n 1. Daily \n\n 2. Conditional \n\n")
        return 1
    await update.message.reply_text("What is the token you would want to set a reminder for? \n\n")
    await get_tokens(update, context)
    return 2

async def type_trigger(update: Update, context: CallbackContext):
    global current_token
    current_token = TOKEN_OPTIONS[int(update.message.text) - 1]
    if not token_check(current_token):
        await update.message.reply_text("Please choose a token from the list\n\n 1. Wrapped Ether (WETH)\n\n 2. Wrapped BTC (WBTC)\n\n 3. ChainLink Token (LINK)\n\n 4. Uniswap (UNI)")
        return 2
    user_id = update.message.chat_id
    if trigger_type == '1':
        await update.message.reply_text("Great! I'll remind you daily about " + current_token + "'s price!")
        add_trigger_daily(user_id, current_token)
        return ConversationHandler.END
    if trigger_type == '2':
        await update.message.reply_text("For " + current_token + " what price point would you want to trigger an alert? \n\n >= input price USD \n\n <= input price USD \n\n")
        return 3

async def price_input(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    user_input = update.message.text
    direction = user_input[0:2]
    if direction not in ['>=', '<=']:
        await update.message.reply_text("Please only choose \n\n >= input price USD \n\n <= input price USD \n\n")
        return 3
    price = user_input[2:]
    if not is_number(price):
        await update.message.reply_text("Please only input numbers \n\n >= input price USD \n\n <= input price USD \n\n")
        return 3
    action = None
    type_of = None
    if direction == '>=':
        action = True
        type_of = 'greater than'
    else:
        action = False
        type_of = 'less than'
    add_trigger_to_db(user_id, current_token, action, price)
    await update.message.reply_text("Great! I'll alert you when " + current_token + "'s price is " + type_of + " $" + price + " USD!")
    return ConversationHandler.END
#Conversation Handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('new_reminder', new_reminder)],
    states= {
        1: [MessageHandler(filters.TEXT, token_select)],
        2: [MessageHandler(filters.TEXT, type_trigger)],
        3: [MessageHandler(filters.TEXT, price_input)]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

def run_async_func(func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(func())
    loop.close()
    return result
#Threading
threading.Thread(target=run_async_func, args=(do_reminders,)).start()
threading.Thread(target=run_async_func, args=(runnning_whale_check,)).start()
threading.Thread(target=run_async_func, args=(do_daily_reminders,)).start()
print("Bot started")
app = Application.builder().token(TELEGRAM_TOKEN).build()

#commands
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('help', help))
app.add_handler(CommandHandler('whale_list', whale_sign_up))
app.add_handler(CommandHandler('tokens', get_tokens))
app.add_handler(CommandHandler('lastPrice', last_price))
app.add_handler(CommandHandler('reminders', get_reminders))
app.add_handler(CommandHandler('remove_whale', remove_whale))
app.add_handler(CommandHandler('cancel', cancel))
# app.add_handler(CallbackQuery(handle_callback))
#conversation
app.add_handler(conv_handler)

app.add_handler(CallbackQueryHandler(handle_button_click))

print("Bot polling.......")
app.run_polling(poll_interval=5)

