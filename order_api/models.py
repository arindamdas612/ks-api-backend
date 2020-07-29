from django.db import models
from shop_api.models import Product
from profiles_api.models import UserProfile
from django.utils.translation import gettext_lazy as _
from datetime import datetime


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PLACED = 'p', _('Placed')
        ACKNOWLEDGED = 'a', _('Acknowledged')
        READY = 'r', _('Ready')
        IN_TRANSIT = 't', _('In Transit')
        DELIVERED = 'w', _('Delivered')
        RETURNED = 'e', _('Returned')
        PARTIAL_RETURN = 'l', _('Partially Returned')
        DISMISSED = 'd', _('Dismissed')

    display_id = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, related_name='order_owner', blank=True)
    status = models.CharField(
        max_length=1, choices=OrderStatus.choices, default=OrderStatus.PLACED)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, related_name='order_updater', blank=True)

    def __str__(self):
        return self.display_id

    def save(self, *args, **kwargs):
        # last_order = self.objects.all().order_by('id').last()
        # time_string = datetime.now().strftime("%y%m%d")
        # if not last_order:
        #     return f'ORD{time_string}00001'
        # order_no = last_order.display_id
        # order_int = int(order_no[-5:])
        # width = 5
        # new_invoice_int = invoice_int + 1
        # formatted = (width - len(str(new_invoice_int))) * \
        #     "0" + str(new_invoice_int)
        # new_order_no = 'ORD' + time_string + str(formatted)
        # self.display_id = new_order_no
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    class OrderItemStatus(models.TextChoices):
        INCART = 'i', _('In-Cart')
        WISHLIST = 'w', _('Wishlisted')
        ORDERED = 'o', _('Ordered')
        DELIVERED = 'd', _('Delivered')
        CANCELLED = 'c', _('Cancelled')
    linked_order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, related_name='owner')
    status = models.CharField(
        max_length=1, choices=OrderItemStatus.choices, default=OrderItemStatus.INCART)
    associated_product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True)
    product_title = models.CharField(max_length=50, blank=True)
    price = models.FloatField(blank=True)
    qty = models.IntegerField(blank=True)
    total_price = models.FloatField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, related_name='item_updater', blank=True)

    def __str__(self):
        return f'{self.associated_product.title} x {self.qty} - {self.get_status_display()}'

    def save(self, *args, **kwargs):
        self.product_title = self.associated_product.title
        self.price = self.associated_product.marked_price
        self.total_price = self.qty * self.associated_product.marked_price
        super().save(*args, **kwargs)
