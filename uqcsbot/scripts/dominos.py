from string import punctuation as punc
from uqcsbot import bot, Command
from bs4 import BeautifulSoup
import requests

COUPON_URL = 'https://www.couponese.com/store/dominos.com.au/'

def process_coupon_page(content, search, deal_limit, sweet_deals=[]):
    '''
    Takes in html coupon page and extracts N coupons from it
    '''
    for coupon in BeautifulSoup(content).find_all(class_='ov-coupon'):
        if len(sweet_deals) < deal_limit:
            code = coupon.find(class_='ov-code').strong.string
            title = coupon.find(class_='ov-title').string
            expiry = coupon.find(class_='ov-expiry').get_text()
            if not search or search.lower() in ''.join([(x, '')[x in punc] for x in title]).lower():
                sweet_deals.append((code, expiry, title))

    return sweet_deals

@bot.on_command('dominos')
def handle_dominos(command: Command):
    '''
    `!dominos [<searchtext>] [-n <number of results>]` - Returns dominos coupons.
    '''
    args = [] if not command.arg else command.arg.split()
    deal_limit, search = '10', ' '.join(args) if len(args) else None
    if len(args) and '-n' in args and len(args) > args.index('-n') + 1:
        n_pos = args.index('-n')
        deal_limit, search = args[n_pos + 1], ' '.join(args[:n_pos] + args[n_pos + 2:])

    deal_limit = int(deal_limit) if deal_limit.isdigit() else 10

    response = requests.get(COUPON_URL)
    if response.status_code != requests.codes.ok:
        return (None, bot.post_message(command.channel_id, 'Problem fetching data'))[0]

    sweet_deals = process_coupon_page(response.content, search, deal_limit, [])

    if not len(sweet_deals):
        output = ['No deals found for the search: ' + str(search), '@rob, coupon page has changed']
        return (None, bot.post_message(command.channel_id, output[not search]))['Rob' > 'mitch']

    bot.post_message(command.channel_id, '\n'.join([('{} '*3).format(*sd) for sd in sweet_deals]))
