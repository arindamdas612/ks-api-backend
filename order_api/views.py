import json
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from .models import Order, OrderItem, OrderActivity, OrderStatus
from .utils import process_order_action, get_updated_order_data, get_update_order_by_id


class OrdersAdminApiView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def get(self, request, format=None):
        response_data = {
            'message_code': 0,
        }
        order_data = get_updated_order_data()
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
                response_data['updated_order_data'] = get_update_order_by_id(
                    order_id)

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
            response_data['updated_order_data'] = get_update_order_by_id(
                order_item.linked_order.id)

            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        except:
            response_data = {
                'message_code': 2,
                'message': 'Could not process the request',
            }
            return Response(response_data, status=status.HTTP_406_NOT_ACCEPTABLE)
