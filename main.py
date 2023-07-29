from typing import Final
from telegram import Bot, Update
import requests
import schedule
import threading
import time
from supabase_py import create_client, Client
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes,Updater, CallbackContext,ConversationHandler

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
  




# url: str = "your-supabase-url"
# key: str = "your-supabase-key"
# supabase: Client = create_client(url, key)



def fetch_token_prices():
    response = requests.get('https://api.gmx.io/tokens')
    tokens = response.json()
    token_prices = {}
    for token in tokens:
        token_prices[token['data']['symbol']] = int(token['data']['liqMaxPrice'])/10**30
        print(token['data']['symbol'], token['data']['name'], int(token['data']['liqMaxPrice'])/10**30)
    return token_prices


# # updater = Updater(TELEGRAM_TOKEN, True)
# # dispatcher = updater.dispatcher
# def add_trigger(update: Update, context: CallbackContext):
#     user_id = update.effective_chat.id
#     token = context.args[0]
#     action = context.args[1]
#     price = float(context.args[2])
#     add_trigger_to_db(user_id, token, action, price)
#     context.bot.send_message(chat_id=user_id, text='Trigger added successfully.')


# def add_trigger_to_db(user_id, token, action, price):
#     trigger = {"token": token, "action": action, "price": price, "user": user_id}
#     supabase.table("triggers").insert(trigger)

# add_trigger_handler = CommandHandler('addtrigger', add_trigger)
# # dispatcher.add_handler(add_trigger_handler)


# def notify_user(user_id, token):
#     bot = Bot(token=TELEGRAM_TOKEN)
#     bot.send_message(chat_id=user_id, text=f'The price of the {token} token has reached your trigger price.')


# def check_triggers():
#     triggers = supabase.table("triggers").select().execute()
#     token_prices = fetch_token_prices()

#     for trigger in triggers['data']:
#         if ((trigger['action'] == 'greater than or equal to' and token_prices[trigger['token']] >= trigger['price']) or 
#            (trigger['action'] == 'less than or equal to' and token_prices[trigger['token']] <= trigger['price'])):
#             notify_user(trigger['user'], trigger['token'])


# def check_prices(update: Update, context: CallbackContext):
#     user_id = update.effective_chat.id
#     check_triggers()
#     context.bot.send_message(chat_id=user_id, text='Checked prices.')



# check_prices_handler = CommandHandler('checkprices', check_prices)
# # dispatcher.add_handler(check_prices_handler)


# # updater = Updater(TELEGRAM_TOKEN, True)
# # disp = updater.dispatcher

current_name = None
current_date = None
def start(update,context):
    update.message.reply_text("Hi! I'm a bot that will help you to keep track of your crypto portfolio. \n\n")

def new_reminder(update,context):
    update.message.reply_text("Whose birthday shall i suck? \n\n")
    return 1
def get_name(update,context):
    global current_name
    current_name = update.message.text
    update.message.reply_text("When do you want to be reminded? \n\n")
    return 2
def get_date(update,context):
    global current_date
    current_date = update.message.text
    update.message.reply_text("Great! I'll remind you on " + current_date + " about " + current_name + "'s birthday!")
    user_id = update.message.chat_id
    print(user_id)
    return ConversationHandler.END
def cancel():
    pass
def do_reminders():
    while True:
        fetch_token_prices()

        time.sleep(100)
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('new', new_reminder)],
    states={
        1: [MessageHandler(filters.TEXT, get_name)],
        2: [MessageHandler(filters.TEXT, get_date)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
threading.Thread(target=do_reminders).start()

print("Bot started")
app = Application.builder().token(token=TELEGRAM_TOKEN).build()

#commands
app.add_handlers(CommandHandler('start', start))
#conversation
app.add_handlers(conv_handler)



print("Bot polling.......")
app.run_polling(poll_interval=30)