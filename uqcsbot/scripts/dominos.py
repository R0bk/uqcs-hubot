from string import punctuation as punc
from uqcsbot import bot, Command
from bs4 import BeautifulSoup
import requests
import json


@bot.on_command("dominos")
def handle_dominos(command: Command):
    '''
    `!dominos [<searchtext>] [-n <number of results>]` - Returns dominos coupons.
    '''

    input_str = command.arg
    deal_limit, search_text = 10, None
    if input_str is not None and input_str.strip() != '':
        args = input_str.split()
        if '-n' in args and len(args) > args.index('-n') + 1:
            n_pos = args.index('-n')
            deal_limit, search_text = args[n_pos + 1], ' '.join(args[:n_pos] + args[n_pos + 2:])
        else:
            deal_limit, search_text = 10, input_str

        deal_limit = int(deal_limit) if deal_limit.isdigit() else 10

    response = requests.get("https://www.couponese.com/store/dominos.com.au/")
    if response.status_code != requests.codes.ok:
        bot.post_message(command.channel_id, "Problem fetching data")
        return

    content = response.content
    soup = BeautifulSoup(content)

    sweet_deals = []

    for coupon in soup.find_all(class_='ov-coupon'):
        code = coupon.find(class_='ov-code').strong.string
        title = coupon.find(class_='ov-title').string
        expiry = coupon.find(class_='ov-expiry').get_text()
        if search_text is None:
            sweet_deals.append((code, expiry, title))
        elif search_text.lower() in title.translate(str.maketrans({c: None for c in punc})).lower():
            sweet_deals.append((code, expiry, title))
        
        if len(sweet_deals) >= deal_limit:
            break

    if len(sweet_deals) == 0:
        if search_text is None:
            bot.post_message(command.channel_id, "@rob, coupon page has changed")
            return
        bot.post_message(command.channel_id, "No deals found for the search: " + search_text)
        return

    bot.post_message(command.channel_id, '\n'.join([('{} '*3).format(*sd) for sd in sweet_deals]))
