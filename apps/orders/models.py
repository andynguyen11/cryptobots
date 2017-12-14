from datetime import datetime, timedelta

import gdax
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings

from bots.buyer import buy
from bots.seller import sell

gdax_client = gdax.AuthenticatedClient(settings.GDAX_KEY, settings.GDAX_SECRET, settings.GDAX_API_PASS)

class Order(models.Model):
    #TODO User based orders
    date_created = models.DateTimeField(auto_now=True)
    product = models.CharField(max_length=50)
    gdax_id = models.CharField(max_length=128)
    status = models.CharField(max_length=50)
    settle = models.BooleanField(default=False)
    size = models.DecimalField(max_digits=15, decimal_places=8)
    price = models.CharField(max_digits=15, decimal_places=8)
    fee = models.CharField(max_digits=15, decimal_places=8)
    reaction = models.CharField(max_length=50)


@receiver(pre_save, sender=Order)
def order_pre_save(sender, instance, **kwargs):
    if not hasattr(instance, 'id') or instance.id is None:
        return
    old_order = Order.objects.get(id=instance.id)
    today = datetime.utcnow()
    if instance.settle and not old_instance.settle:
        accounts = gdax_client.get_accounts()
        usd_wallet = (account for account in accounts if account["currency"] == "USD").next()
        if reaction is 'buy':
            buy()
