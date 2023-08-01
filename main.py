from typing import Final
from telegram import Bot, Update
import requests
import threading
import time
from supabase import create_client, Client
import os 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes,Updater, CallbackContext,ConversationHandler
from dotenv import load_dotenv
import asyncio

# [{"id":"0x17FC002b466eEc40DaE837Fc4bE5c67993ddBd6F","data":{"symbol":"FRAX","reservedAmount":"378077560981592079166440","liqMinPrice":"999000020000000000000000000000","address":"0x17FC002b466eEc40DaE837Fc4bE5c67993ddBd6F","poolAmount":"10999999987248385879937667","globalShortSize":"0","weight":"2000","redemptionAmount":"1000000000000000000000000000000","liqMaxPrice":"999000020000000000000000000000","maxGlobalLongSize":"0","bufferAmount":"1000000000000000000000000","availableAmount":"10621922426266793800771227","decimals":18,"minPrice":"1000000000000000000000000000000","guaranteedUsd":"0","name":"Frax","maxUsdgAmount":"11000000000000000000000000","cumulativeFundingRate":"60584","maxPrice":"1000000000000000000000000000000","usdgAmount":"10999999987248385879937667","maxGlobalShortSize":"0","fundingRate":"3","updatedAt":1690584633}},
#  {"id":"0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f","data":{"symbol":"WBTC","reservedAmount":"84576267163","liqMinPrice":"29297736000000000000000000000000000","address":"0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f","poolAmount":"408894400784","globalShortSize":"8476638729118489157912229081278068465","weight":"25000","redemptionAmount":"3413084605930371","liqMaxPrice":"29297736000000000000000000000000000","maxGlobalLongSize":"35773295412798245898515614858911619627","bufferAmount":"250000000000","availableAmount":"324318133621","decimals":8,"minPrice":"29299010000000000000000000000000000","guaranteedUsd":"22254099312660715822578720908483251010","name":"Wrapped Bitcoin","maxUsdgAmount":"140000000000000000000000000","cumulativeFundingRate":"481959","maxPrice":" ","usdgAmount":"116543544374870520546113471","maxGlobalShortSize":"19526072096941042536124121532909733205","fundingRate":"20","updatedAt":1690584633}},
#  {"id":"0x82aF49447D8a07e3bd95BD0d56f35241523fBab1","data":{"symbol":"ETH","reservedAmount":"20019220331180981054064","liqMinPrice":"1876445600000000000000000000000000","address":"0x82aF49447D8a07e3bd95BD0d56f35241523fBab1","poolAmount":"68471525662776002434589","globalShortSize":"20542683327230213053665740135592917078","weight":"30000","redemptionAmount":"533000740871029810731436916","liqMaxPrice":"1876445600000000000000000000000000","maxGlobalLongSize":"45285580330546351132904934067280286335","bufferAmount":"60000000000000000000000","availableAmount":"48452305331595021380525","decimals":18,"minPrice":"1876170000000000000000000000000000","guaranteedUsd":"33389068193085704813739782344043159440","name":"Ethereum","maxUsdgAmount":"155000000000000000000000000","cumulativeFundingRate":"626149","maxPrice":"1876170000000000000000000000000000","usdgAmount":"123035580193208588411105983","maxGlobalShortSize":"25793460367058138613345722013892012527","fundingRate":"29","updatedAt":1690584633}},
#  {"id":"0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1","data":{"symbol":"DAI","reservedAmount":"1949994062450423207576965","liqMinPrice":"1000000000000000000000000000000","address":"0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1","poolAmount":"33551424591082137011386458","globalShortSize":"0","weight":"5000","redemptionAmount":"1000000000000000000000000000000","liqMaxPrice":"1000000000000000000000000000000","maxGlobalLongSize":"0","bufferAmount":"7000000000000000000000000","availableAmount":"31601430528631713803809493","decimals":18,"minPrice":"1000000000000000000000000000000","guaranteedUsd":"0","name":"Dai","maxUsdgAmount":"39000000000000000000000000","cumulativeFundingRate":"138487","maxPrice":"1000000000000000000000000000000","usdgAmount":"33558520854336955802808838","maxGlobalShortSize":"0","fundingRate":"5","updatedAt":1690584633}},
#  {"id":"0xFEa7a6a0B346362BF88A9e4A88416B77a57D6c2A","data":{"symbol":"MIM","reservedAmount":"0","liqMinPrice":"991901250000000000000000000000","address":"0xFEa7a6a0B346362BF88A9e4A88416B77a57D6c2A","poolAmount":"364804879013815250","globalShortSize":"0","weight":"1","redemptionAmount":"1000000000000000000000000000000","liqMaxPrice":"991901250000000000000000000000","maxGlobalLongSize":"0","bufferAmount":"0","availableAmount":"364804879013815250","decimals":18,"minPrice":"991901250000000000000000000000","guaranteedUsd":"0","name":"Magic Internet Money","maxUsdgAmount":"1000000000000000000","cumulativeFundingRate":"25032","maxPrice":"1000000000000000000000000000000","usdgAmount":"356877394819954755","maxGlobalShortSize":"0","fundingRate":"0","updatedAt":1690584633}},
#  {"id":"0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8","data":{"symbol":"USDC.e","reservedAmount":"24281215313479","liqMinPrice":"1000191360000000000000000000000","address":"0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8","poolAmount":"181832881049542","globalShortSize":"0","weight":"32000","redemptionAmount":"1000000000000000000","liqMaxPrice":"1000191360000000000000000000000","maxGlobalLongSize":"0","bufferAmount":"150000000000000","availableAmount":"157551665736063","decimals":6,"minPrice":"1000000000000000000000000000000","guaranteedUsd":"0","name":"Bridged USDC","maxUsdgAmount":"220000000000000000000000000","cumulativeFundingRate":"381974","maxPrice":"1000000000000000000000000000000","usdgAmount":"181868228993477858739444718","maxGlobalShortSize":"0","fundingRate":"13","updatedAt":1690584633}},
#  {"id":"0xFa7F8980b0f1E64A2062791cc3b0871572f1F7f0","data":{"symbol":"UNI","reservedAmount":"66350717231068532548652","liqMinPrice":"6009700000000000000000000000000","address":"0xFa7F8980b0f1E64A2062791cc3b0871572f1F7f0","poolAmount":"581645935434261114588904","globalShortSize":"332691134353945033946715542636567500","weight":"1000","redemptionAmount":"166389351081530782029950083194","liqMaxPrice":"6009700000000000000000000000000","maxGlobalLongSize":"500000000000000000000000000000000000","bufferAmount":"400000000000000000000000","availableAmount":"515295218203192582040252","decimals":18,"minPrice":"6010000000000000000000000000000","guaranteedUsd":"319337425518780505751009692103979649","name":"Uniswap","maxUsdgAmount":"5000000000000000000000000","cumulativeFundingRate":"182659","maxPrice":"6010000000000000000000000000000","usdgAmount":"3294574164350380076446018","maxGlobalShortSize":"500000000000000000000000000000000000","fundingRate":"11","updatedAt":1690584633}},
#  {"id":"0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9","data":{"symbol":"USDT","reservedAmount":"1362837487540","liqMinPrice":"999900000000000000000000000000","address":"0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9","poolAmount":"8202612422817","globalShortSize":"0","weight":"2000","redemptionAmount":"1000000000000000000","liqMaxPrice":"999900000000000000000000000000","maxGlobalLongSize":"0","bufferAmount":"1000000000000","availableAmount":"6839774935277","decimals":6,"minPrice":"1000000000000000000000000000000","guaranteedUsd":"0","name":"Tether","maxUsdgAmount":"8200000000000000000000000","cumulativeFundingRate":"419434","maxPrice":"1000000000000000000000000000000","usdgAmount":"8199999908206967998008876","maxGlobalShortSize":"0","fundingRate":"16","updatedAt":1690584633}},
#  {"id":"0xaf88d065e77c8cC2239327C5EDb3A432268e5831","data":{"symbol":"USDC","reservedAmount":"1812034569678","liqMinPrice":"1000191360000000000000000000000","address":"0xaf88d065e77c8cC2239327C5EDb3A432268e5831","poolAmount":"9125424677771","globalShortSize":"0","weight":"2000","redemptionAmount":"1000000000000000000","liqMaxPrice":"1000191360000000000000000000000","maxGlobalLongSize":"0","bufferAmount":"1000000000000","availableAmount":"7313390108093","decimals":6,"minPrice":"1000000000000000000000000000000","guaranteedUsd":"0","name":"USD Coin","maxUsdgAmount":"20000000000000000000000000","cumulativeFundingRate":"18008","maxPrice":"1000000000000000000000000000000","usdgAmount":"9120375607848606248417728","maxGlobalShortSize":"0","fundingRate":"19","updatedAt":1690584633}},
#  {"id":"0xf97f4df75117a78c1A5a0DBb814Af92458539FB4","data":{"symbol":"LINK","reservedAmount":"100045005477550699731145","liqMinPrice":"7821977830000000000000000000000","address":"0xf97f4df75117a78c1A5a0DBb814Af92458539FB4","poolAmount":"532819187309970490044192","globalShortSize":"428422169662076156785256500647662316","weight":"1000","redemptionAmount":"128008192524321556579621095750","liqMaxPrice":"7821977830000000000000000000000","maxGlobalLongSize":"500000000000000000000000000000000000","bufferAmount":"450000000000000000000000","availableAmount":"432774181832419790313047","decimals":18,"minPrice":"7812000000000000000000000000000","guaranteedUsd":"499990231165838851355313941133155949","name":"Chainlink","maxUsdgAmount":"6100000000000000000000000","cumulativeFundingRate":"426911","maxPrice":"7812000000000000000000000000000","usdgAmount":"3784870023987995387479687","maxGlobalShortSize":"500000000000000000000000000000000000","fundingRate":"18","updatedAt":1690584633}}]

TELEGRAM_TOKEN: Final= '6396994222:AAG7p2O9wkZH5ZPxMI3WR4nvUzXcEpnOj3s'
BOT_USERNAME: Final = '@banana_man_do_bot'

            # "chat_id": "5000177235",
  
dotenv_path = './.env'
load_dotenv(dotenv_path=dotenv_path)

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)



#Helper functions
def token_check(token):
    token_to_check = token.upper()
    if token_to_check in TOKEN_OPTIONS:
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

async def notify_user(user_id, token,price,new_price,actionType):
    typeOf = None
    if actionType == True:
        typeOf = 'greater than'
    else:
        typeOf = 'less than'
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=user_id, text=f'Alert!\nThe price of {token} is {typeOf} your trigger price of ${price}.\n Current Price is ${new_price}')




#Database
#db push
def add_trigger_daily(user_id, token:str):
    token_input = token.upper()
    print('token inmput',token_input)
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
def add_user_to_db(user_id):
    user = {"user_chatid": user_id}
    try:
        supabase.table("users").upsert(user).execute()
    except Exception as e:
        print('error',e)
#db pull
def get_untriggered_reminders(user_id):
    try:
        response = supabase.table("triggers").select("token, type, price, action_greater,created_at").eq('user_id', user_id).neq('has_reminded', True).execute()
    except:
        print('error')
    try:
        response2 = supabase.table("triggers").select("token, type, price, action_greater,created_at").eq('user_id', user_id).eq('type', 'daily').execute()
    except:
        print('error')
    triggers = response.data
    triggers.extend(response2.data)
    print(triggers)
    for trigger in triggers:
        if trigger['type'] == 'daily':
            print('daily')
            print(trigger['token'])
            print(trigger['created_at'])
        if trigger['type'] == 'conditional':
            print('conditional')
            print(trigger['token'])
            print(trigger['price'])
            print(trigger['action_greater'])
            print(trigger['created_at'])


async def check_triggers(token,action,new_price):
    token = token.upper()
    try:
        if action == True:
            response = supabase.table("triggers").select("price, user_id,id").eq('token', token).eq('action_greater', action).eq('has_reminded',False).lte('price', new_price).execute()
        else:
            response = supabase.table("triggers").select("price, user_id,id").eq('token', token).eq('action_greater', action).eq('has_reminded',False).gte('price', new_price).execute()
    except:
        print('error')
    triggers = response.data
    for trigger in triggers:
        print(trigger)
        await notify_user(trigger['user_id'], token, trigger['price'], new_price, action)
        db_triggered(trigger['id'])

#Global Variables
TOKEN_OPTIONS= ['FRAX','WBTC','ETH','DAI','MIM','UNI','USDC.E','USDT','LINK']
LAST_TOKEN_PRICE = {}
PREV_TOKEN_PRICES = {}
PRICE_CHANGES = {}
current_token = None
trigger_type = None


#Getting Prices and Checking DB
async def do_reminders():
    while True:
        await fetch_token_prices()

        time.sleep(30)

#Http requests
async def fetch_token_prices():
    response = requests.get('https://api.gmx.io/tokens')
    tokens = response.json()
    token_prices = {}
    PREV_TOKEN_PRICES = LAST_TOKEN_PRICE.copy()
    LAST_TOKEN_PRICE.clear()
    PRICE_CHANGES.clear()
    for token in tokens:
        token_prices[token['data']['symbol']] = int(token['data']['minPrice'])/10**30
        LAST_TOKEN_PRICE[token['data']['symbol']] = int(token['data']['minPrice'])/10**30
        if token['data']['symbol'] in PREV_TOKEN_PRICES:
            # If the price has increased, store 'up', otherwise store 'down'
            if int(token['data']['minPrice'])/10**30 > PREV_TOKEN_PRICES[token['data']['symbol']]:
                PRICE_CHANGES[token['data']['symbol']] = 'up'
            # if int(token['data']['minPrice'])/10**30 == PREV_TOKEN_PRICES[token['data']['symbol']]: 
            #     print('same')
            if int(token['data']['minPrice'])/10**30 < PREV_TOKEN_PRICES[token['data']['symbol']]:
                PRICE_CHANGES[token['data']['symbol']] = 'down'
        # print(token['data']['symbol'], token['data']['name'], int(token['data']['minPrice'])/10**30)
    await check_change()
    return token_prices


#Commands
async def start(update: Update,context):
    await update.message.reply_text("Hi! I'm a bot that will help you to keep track of your crypto portfolio. \n\n We track token prices on GMX \n\n To get started, type /new_reminder \n\n Type /tokens to get a list of tokens you can track \n\n Type /lastPrice to get the last price of all the tokens \n\n Type /reminders to get a list of your reminders \n\nType /cancel anytime to end conversation ")
async def help(update: Update,context):
    await update.message.reply_text("Hi! I'm a bot that will help you to keep track of your crypto portfolio. \n\n We track token prices on GMX \n\n To get started, type /new_reminder \n\n Type /tokens to get a list of tokens you can track \n\n Type /lastPrice to get the last price of all the tokens \n\nType /reminders to get a list of your reminders \n\nType /cancel anytime to end conversation")
async def get_tokens(update: Update,context):
    await update.message.reply_text("Here are the list of tokens you have the option of tracking \n\n 1. FRAX \n\n 2. WBTC \n\n 3. ETH \n\n 4. DAI \n\n 5. MIM \n\n 6. UNI \n\n 7. USDC.E \n\n 8. USDT \n\n 9. LINK \n\n") 
async def last_price(update: Update,context):
    # Assuming LAST_TOKEN_PRICE is your dictionary
    token_prices_str = '\n'.join(f'{k}: {v}' for k, v in LAST_TOKEN_PRICE.items())
    await update.message.reply_text("Here are the lastet prices: \n\n" + token_prices_str)
    return ConversationHandler.END    
async def get_reminders(update: Update,context):
    await update.message.reply_text("Here are your reminders: \n\n") 
    get_untriggered_reminders(update.message.chat_id)
    return ConversationHandler.END
#Entry Point
async def new_reminder(update: Update,context):
    user_id = update.message.chat_id
    add_user_to_db(user_id)
    await update.message.reply_text("Please choose your reminder \n\n 1. Daily \n\n 2. Conditional \n\n")
    return 1
#Conversations
async def token_select(update: Update,context):
    global trigger_type
    trigger_type = update.message.text
    if trigger_type not in ['1','2']:
        await update.message.reply_text("Please only choose \n\n 1. Daily \n\n 2. Conditional \n\n")
        return 1
    await update.message.reply_text("What is the token you would want to set a reminder for? \n\n")
    await get_tokens(update,context)
    return 2
async def type_trigger(update: Update,context):
    global current_token
    current_token = update.message.text.upper()
    if not token_check(current_token):
        await update.message.reply_text("Please choose a token from the list\n\n 1. FRAX \n\n 2. WBTC \n\n 3. ETH \n\n 4. DAI \n\n 5. MIM \n\n 6. UNI \n\n 7. USDC.E \n\n 8. USDT \n\n 9. LINK \n\n")
        return 2
    user_id = update.message.chat_id
    if trigger_type == '1':
        await update.message.reply_text("Great! I'll remind you daily about "+" " + current_token + "'s price!")
        add_trigger_daily(user_id, current_token)
        return ConversationHandler.END
    if trigger_type == '2':  
        await update.message.reply_text("For " + current_token + " what price point would you want to trigger an alert? \n\n >= input price USD \n\n <= input price USD \n\n")
        return 3

async def price_input(update: Update,context):
    user_id = update.message.chat_id
    user_input = update.message.text
    direction = user_input[0:2]
    if direction not in ['>=','<=']:
        await update.message.reply_text("Please only choose \n\n >= input price USD \n\n <= input price USD \n\n")
        return 3
    price = user_input[2:]
    if not is_number(price):
        await update.message.reply_text("Please only input numbers \n\n >= input price USD \n\n <= input price USD \n\n")
        return 3
    action = None
    typeOF = None
    if direction == '>=':
        action = True
        typeOF = 'greater than or equal to'
    else:
        action = False
        typeOF = 'less than or equal to'
    add_trigger_to_db(user_id, current_token, action, price)
    await update.message.reply_text("Great! I'll alert you when " + current_token + "'s price is " + typeOF + "  $" + price + " USD!")
    return ConversationHandler.END   
async def cancel(update: Update,context):
    print("cancel")
    await update.message.reply_text('Conversation cancelled.')
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

print("Bot started")
app = Application.builder().token(TELEGRAM_TOKEN).build()

#commands
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('help', help))
app.add_handler(CommandHandler('tokens', get_tokens))
app.add_handler(CommandHandler('lastPrice', last_price))
app.add_handler(CommandHandler('reminders', get_reminders))
app.add_handler(CommandHandler('cancel', cancel))
#conversation
app.add_handler(conv_handler)


print("Bot polling.......")
app.run_polling(poll_interval=5)
