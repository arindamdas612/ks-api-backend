from django.db import models
from shop_api.models import Product, ProductImage
from profiles_api.models import UserProfile
from django.utils.translation import gettext_lazy as _
from datetime import datetime


class OrderStatus(models.TextChoices):
    PLACED = 'p', _('Placed')
    ACKNOWLEDGED = 'a', _('Acknowledged')
    READY = 'r', _('Ready')
    IN_TRANSIT = 't', _('In Transit')
    DELIVERED = 'w', _('Delivered')
    RETURNED = 'e', _('Returned')
    PARTIAL_NOSTOCK = 's', _('No Stock (P)')
    NOSTOCK = 'X', _('No Stock')
    DISMISSED = 'd', _('Dismissed')


class Order(models.Model):

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

    def next_actions(self, *args, **kwargs):
        if self.get_status_display() == 'Placed':
            return ['Acknowledged', 'Dismissed',  'No Stock', 'No Stock (P)', ]
        if self.get_status_display() == 'Acknowledged' or self.get_status_display() == 'No Stock (P)':
            return ['Ready', 'Dismissed']
        if self.get_status_display() == 'Ready':
            return ['In Transit', 'Dismissed']
        if self.get_status_display() == 'In Transit':
            return ['Delivered', 'Dismissed']

        return []

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
        INCART = 'i', _('In Cart')
        WISHLIST = 'w', _('Wishlisted')
        INPROCESS = 'p', _('In Process')
        NOSTOCK = 'n', _('No Stock')
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

    def get_cover_image(self, *args, **kwargs):
        image_url = None
        if self.associated_product:
            cover_image = ProductImage.objects.filter(
                product=self.associated_product).first()
            image_url = cover_image.get_image_url()
        return image_url

    def should_change_status(self, *args, **kwargs):
        update = True
        if self.get_status_display() == 'No Stock':
            update = False
        return update


class OrderActivity(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    prev_status = models.CharField(
        max_length=1, choices=OrderStatus.choices)
    next_status = models.CharField(
        max_length=1, choices=OrderStatus.choices)
    changed_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    changed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.display_id} from {self.prev_status} to {self.next_status}"
