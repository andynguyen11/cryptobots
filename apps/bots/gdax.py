import time
import gdax

from django.conf import settings

from orders.models import Order


class Autobot(object):

    def __init__(self):
        self.gdax_client = gdax.AuthenticatedClient(settings.GDAX_KEY, settings.GDAX_SECRET, settings.GDAX_API_PASS, settings.GDAX_API_URL)
        self.accounts = gdax_client.get_accounts()
        self.usd_wallet = (account for account in self.accounts if account["currency"] == "USD").next()

    def buy(self, product, order, market=True):
        """
        Send buy order to gdax

        :param product:
        :param market:
        :return order instance:
        """
        coin_buy = self.gdax_client.buy(
            price=coin['ask'],
            size=usd_wallet['available']/coin['ask'],
            product_id=product,
            #type='limit',
            #post_only=True
        )
        order = Order(
            gdax_id=coin_buy['id'],
            status=coin_buy['status'],
            settled=coin_buy['settled'],
            size=coin_buy['size']
        )
        order.save()
        return order

    def sell(self, product, order, market=True):
        """
        Send sell order to gdax

        :param product:
        :param market:
        :return order instance:
        """
        coin_sell = self.gdax_client.sell(
            price=coin['ask'],
            size=order.size,
            product_id=product,
            #type='limit',
            #post_only=True
        )
        order = Order(
            status=coin_sell['status'],
            settled=coin_sell['settled'],
            size=coin_sell['size']
        )
        order.save()
        return order

    def triangulate(self):
        """
        Buy/sell disparity triangle

        :return:
        """
        pass

    def monitor(self, id):
        """
        Monitors order and updates on changes

        :return:
        """
        order = Order.objects.get(id=id)
        gdax_order = gdax_client.get_order(order.gdax_id)
        if gdax_order['settled']:
            order.settled = gdax_order['settled']
            order.stats = gdax_order['stats']
            order.save()

    def save_order(self, order):
        """
        Save gdax order to Order model

        :param order:
        :return order instance:
        """
        pass

    def get_order(self, id):
        """
        Get order

        :param id
        :return order instance:
        """
        pass

    def price_check(self):
        """
        Returns prices of products from gdax api

        :return price dict:
        """
        prices = {
            'eth_btc': self.gdax_client.get_product_ticker(product_id='ETH-BTC'),
            'ltc_btc': self.gdax_client.get_product_ticker(product_id='LTC-BTC'),
            'eth': self.gdax_client.get_product_ticker(product_id='ETH-USD'),
            'ltc': self.gdax_client.get_product_ticker(product_id='LTC-USD'),
            'btc': self.gdax_client.get_product_ticker(product_id='BTC-USD')
        }
        return prices

    def calculate_disparity(self, product):
        """
        Calculates the exchange disparity between coins

        :param product:
        :return disparity dict:
        """
        #TODO Make dynamic based on product.  86 the hardcode ya fuck.
        prices = self.price_check()
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