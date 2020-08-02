import json

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from .models import Order, OrderItem, OrderActivity, OrderStatus
from .utils import process_order_action


class OrdersAdminApiView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def get(self, request, format=None):
        response_data = {
            'message_code': 0,
        }
        order_data = []

        all_orders = Order.objects.all().order_by('-created_on')
        for order in all_orders:
            order_item_data = []
            order_activity_data = [{
                'id': -1,
                'prev_status': 'Unavailable',
                'next_status': 'Placed',
                'activity_dt': order.created_on.isoformat(),
                'user': order.user.get_full_name(),
                'is_admin': order.user.is_superuser,
            }]
            order_value = 0
            order_items = OrderItem.objects.filter(linked_order__id=order.id)
            order_activities = OrderActivity.objects.filter(order__id=order.id)
            for oi in order_items:
                order_value += oi.total_price
                item = {
                    'id': oi.id,
                    'product_title': oi.product_title,
                    'qty': oi.qty,
                    'unit_price': oi.price,
                    'status': oi.get_status_display(),
                    'image_URL': oi.get_cover_image(),
                    'total_price': oi.total_price,
                }
                order_item_data.append(item)

            for ord_act in order_activities:
                activity_item = {
                    'id': ord_act.id,
                    'prev_status': ord_act.prev_status,
                    'next_status': ord_act.next_status,
                    'activity_dt': ord_act.changed_on.isoformat(),
                    'user': ord_act.changed_by.get_full_name(),
                    'is_admin': ord_act.changed_by.is_superuser,
                }
                order_activity_data.append(activity_item)
            ord = {
                'id': order.id,
                'display_id': order.display_id,
                'user_name': order.user.get_full_name(),
                'user_mobile': order.user.mobile,
                'user_email': order.user.email,
                'order_value': order_value,
                'order_items': order_item_data,
                'order_activity': order_activity_data,
                'status': order.get_status_display(),
                'created_on': order.created_on.isoformat(),
                'update_on': order.updated_on.isoformat(),
                'order_dt': order.created_on.strftime("%m/%d/%Y"),
                'available_actions': order.next_actions(),
            }

            order_data.append(ord)
        response_data['message_code'] = 1
        response_data['orders'] = order_data
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        response_data = {
            'message_code': 0,
        }

        try:
            order_id = request.data.get('id')
            next_status = request.data.get('status')

            processed_data = process_order_action(
                next_status=next_status, order_id=order_id, user=request.user)
            response_data['message_code'] = processed_data[0]
            response_data['message'] = processed_data[1]
            if processed_data[0] == 0:
                response_data['order_items'] = processed_data[2]
                response_data['available_actions'] = processed_data[3]
                response_data['order_activities'] = processed_data[4]

                ret_status = status.HTTP_205_RESET_CONTENT
            else:
                ret_status = status.HTTP_400_BAD_REQUEST
            return Response(response_data, status=ret_status)
        except:
            response_data = {
                'message_code': 2,
                'message': 'Order Action Activity Failed'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, format=None):
        response_data = {
            'message_code': 0,
        }

        try:
            order_item_id = request.data.get('id')
            next_status = request.data.get('nextStatus')

            order_item = OrderItem.objects.get(pk=order_item_id)
            available_actions = ['No Stock', 'Ordered']
            order_status = [OrderStatus.PLACED, OrderStatus.NOSTOCK]
            if order_item.get_status_display() not in available_actions or order_item.linked_order.status == OrderStatus.NOSTOCK:
                response_data['message_code'] = 1
                response_data['message'] = 'Item Status change Failed'
                return Response(response_data, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            if next_status == 'No Stock':
                order_item.status = OrderItem.OrderItemStatus.NOSTOCK
            else:
                order_item.status = OrderItem.OrderItemStatus.ORDERED

            order_item.save()
            response_data['order_id'] = order_item.linked_order.id
            response_data['changed_status'] = order_item.get_status_display()

            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        except:
            response_data = {
                'message_code': 2,
                'message': 'Could not process the request',
            }
            return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)
