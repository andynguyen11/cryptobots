import time
import gdax

from django.conf import settings

gdax_client = gdax.AuthenticatedClient(settings.GDAX_KEY, settings.GDAX_SECRET, settings.GDAX_API_PASS, settings.GDAX_API_URL)
accounts = gdax_client.get_accounts()
usd_wallet = (account for account in accounts if account["currency"] == "USD").next()

def price_check():
    prices = {
        'eth_btc': gdax_client.get_product_ticker(product_id='ETH-BTC'),
        'ltc_btc': gdax_client.get_product_ticker(product_id='LTC-BTC'),
        'eth': gdax_client.get_product_ticker(product_id='ETH-USD'),
        'ltc': gdax_client.get_product_ticker(product_id='LTC-USD'),
        'btc': gdax_client.get_product_ticker(product_id='BTC-USD')
    }
    return prices

def calculate_disparity():
    prices = price_check()
    print('ETH:', prices['eth_btc']['price'])
    print('LTC:', prices['ltc_btc']['price'])
    print('BTC-USD:', prices['btc']['price'])
    eth_per_btc = float(1)/float(prices['eth_btc']['price'])
    eth_btc_usd = float(eth_per_btc) * float(prices['eth']['price'])
    eth_disparity = float(prices['btc']['price']) - float(eth_btc_usd)
    ltc_per_btc = float(1)/float(prices['ltc_btc']['price'])
    ltc_btc_usd = float(ltc_per_btc) * float(prices['ltc']['price'])
    ltc_disparity = float(prices['btc']['price']) - float(ltc_btc_usd)
    disparity = {
        'eth': eth_disparity,
        'ltc': ltc_disparity
    }
    return disparity

def buy_btc():
    prices = price_check()
    buy = gdax_client.buy(
            price=prices['btc']['ask'],
            size=round(float(usd_wallet['available'])/float(prices['btc']['ask']), 8),
            product_id='BTC-USD',
            type='limit',
            post_only=True
        )

    print('USD Available:', usd_wallet['available'])

    if disparity > 0:
        eth_buy = gdax_client.buy(
            price=eth_usd['ask'],
            size=usd_wallet['available']/eth_usd['ask'],
            product_id='ETH-USD',
            type='limit',
            post_only=True
        )

        while not eth_buy['settled']:
            eth_buy = gdax_client.get_order(eth_buy['id'])
            time.sleep(.3)

        eth_btc_sell = gdax_client.sell(
            price=eth_btc_exchange['ask'],
            size=1,
            product_id='ETH-BTC',
            type='limit',
            post_only=True
        )

        while not eth_btc_buy['settled']:
            eth_btc_sell = gdax_client.get_order(eth_btc_sell['id'])
            time.sleep(.3)

        btc_sell = gdax_client.sell(
            price=btc_usd['ask'],
            size=eth_btc_sell['executed_value'],
            product_id='BTC-USD',
            type='limit',
            post_only=True
        )