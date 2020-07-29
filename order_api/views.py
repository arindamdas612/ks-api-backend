import json

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from .models import Order, OrderItem


class OrdersAdminApiView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def get(self, request, format=None):
        response_data = {
            'message_code': 0,
        }
        order_data = []
        order_value = 0
        all_orders = Order.objects.all().order_by('-created_on')
        for order in all_orders:
            order_item_data = []
            order_items = OrderItem.objects.filter(linked_order__id=order.id)
            for oi in order_items:
                order_value += oi.total_price
                item = {
                    'id': oi.id,
                    'product_title': oi.product_title,
                    'qty': oi.qty,
                    'unit_price': oi.price,
                    'status': oi.get_status_display(),
                    'total_price': oi.total_price,
                }

                order_item_data.append(item)
            ord = {
                'id': order.id,
                'display_id': order.display_id,
                'user_name': order.user.get_full_name(),
                'user_mobile': order.user.mobile,
                'user_email': order.user.email,
                'order_value': order_value,
                'order_items': order_item_data,
                'status': order.get_status_display(),
                'created_on': order.created_on.isoformat(),
                'update_on': order.updated_on.isoformat(),
                'order_dt': order.created_on.strftime("%m/%d/%Y")
            }

            order_data.append(ord)
        response_data['message_code'] = 1
        response_data['orders'] = order_data
        return Response(response_data, status=status.HTTP_200_OK)
