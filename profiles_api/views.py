from rest_framework import status
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from profiles_api import serializers
from profiles_api import models
from profiles_api import permissions

from order_api.models import Order, OrderItem, OrderStatus


class AdminDashboardDatapoints(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def get(self, request, format=None):
        response_data = {
            'message_code': 0
        }
        app_user_count = models.UserProfile.objects.filter(
            is_superuser=False).count()
        response_data['user_count'] = app_user_count

        first_order_date = timezone.localtime(
            Order.objects.all().first().created_on)
        first_order_date = datetime.date(first_order_date)
        days_since_first_order = datetime.date(
            datetime.now()) - first_order_date
        total_order = Order.objects.all().count()
        delivered_order_count = Order.objects.filter(
            status=OrderStatus.DELIVERED).count()
        order_avg = round(days_since_first_order.days/total_order, 2)
        success_rate = f"{round((delivered_order_count/total_order) * 100, 0)} %"

        month_list = {
            'Jan': 1,
            'Feb': 2,
            'Mar': 3,
            'Apr': 4,
            'May': 5,
            'Jun': 6,
            'Jul': 7,
            'Aug': 8,
            'Sep': 9,
            'Oct': 10,
            'Nov': 11,
            'Dec': 12
        }

        month, year = datetime.now().strftime('%b-%Y').split('-')
        month = month_list[month]
        year = int(year)
        current_day = datetime.now().day
        month_begin_date = datetime(year=year, month=month, day=1, hour=0,
                                    minute=0, second=0, microsecond=0, tzinfo=timezone.get_current_timezone())
        day_begin_date = datetime(year=year, month=month, day=current_day, hour=0,
                                  minute=0, second=0, microsecond=0, tzinfo=timezone.get_current_timezone())
        next_month = month + 1
        if next_month > 12:
            next_month = 1
            year = year + 1
        month_end_date = month_begin_date.replace(month=next_month, year=year)
        month_end_date = month_end_date - timedelta(milliseconds=1)
        day_end_date = (day_begin_date + timedelta(days=1)) - \
            timedelta(milliseconds=1)
        order_day_count = Order.objects.filter(
            created_on__lte=day_end_date, created_on__gte=day_begin_date).count()
        order_day = Order.objects.filter(
            created_on__lte=day_end_date, created_on__gte=day_begin_date, status=OrderStatus.DELIVERED)
        order_day_amount = 0
        for o in order_day:
            item_prices = OrderItem.objects.filter(status=OrderItem.OrderItemStatus.DELIVERED, linked_order=o).aggregate(
                Sum('total_price')).get('total_price__sum')
            order_day_amount = order_day_amount + item_prices

        order_month_count = Order.objects.filter(
            created_on__lte=month_end_date, created_on__gte=month_begin_date).count()
        order_month = Order.objects.filter(
            created_on__lte=month_end_date, created_on__gte=month_begin_date, status=OrderStatus.DELIVERED)
        order_month_amount = 0
        for o in order_day:
            item_prices = OrderItem.objects.filter(status=OrderItem.OrderItemStatus.DELIVERED).aggregate(
                Sum('total_price')).get('total_price__sum')

            order_month_amount = order_month_amount + item_prices

        response_data['user_count'] = app_user_count
        response_data['order_avg'] = order_avg
        response_data['success_rate'] = success_rate

        response_data['order_day_amount'] = order_day_amount
        response_data['order_day_count'] = order_day_count

        response_data['order_month_amount'] = order_month_amount
        response_data['order_month_count'] = order_month_count

        return Response(response_data, status=status.HTTP_200_OK)


class UserProfileViewSet(viewsets.ModelViewSet):
    """Handle creating and updating profiles"""
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.UpdateOwnProfile,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'email')


class UserLoginAPIView(ObtainAuthToken):
    """Handle creating user Authentication tokens"""
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserManageApiView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAdminUser,)

    def get(self, request, format=None):
        response_data = {
            'message_code': 0
        }

        users = models.UserProfile.objects.all().order_by('-id')
        user_data = []
        for user in users:
            orders = Order.objects.filter(user=user)
            order_ids = [
                order.id for order in Order.objects.filter(user=user).order_by('-id')]
            cart_items = [{
                'id': oi.id,
                'product_title': oi.product_title,
                'qty': oi.qty,
                'unit_price': oi.price,
                'status': oi.get_status_display(),
                'image_URL': oi.get_cover_image(),
                'total_price': oi.total_price,
            } for oi in OrderItem.objects.filter(user=user, status=OrderItem.OrderItemStatus.INCART).order_by('-id')]
            wishlisted_items = [{
                'id': oi.id,
                'product_title': oi.product_title,
                'qty': oi.qty,
                'unit_price': oi.price,
                'status': oi.get_status_display(),
                'image_URL': oi.get_cover_image(),
                'total_price': oi.total_price,
            } for oi in OrderItem.objects.filter(user=user, status=OrderItem.OrderItemStatus.WISHLIST).order_by('-id')]

            user_data.append({
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email,
                'mobile': user.mobile,
                'is_active': user.is_active,
                'is_admin': user.is_superuser,
                'orders': order_ids,
                'cart_items': cart_items,
                'wishlisted_items': wishlisted_items,
            })
        response_data['users'] = user_data

        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        response_data = {
            'message_code': 0
        }
        action = request.data.get('actionType')
        user_id = request.data.get('userId')
        rec_processed = False
        user = models.UserProfile.objects.get(pk=user_id)

        if action == 'STATUS':
            rec_processed = True
            user.is_active = not user.is_active
            user.save()
            response_data['message'] = 'User status changed'

        if not rec_processed:
            response_data['message'] = 'Unidentified Action'
            response_data['message_code'] = 1
            return Response(response_data, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        orders = Order.objects.filter(user=user)
        order_ids = [
            order.id for order in Order.objects.filter(user=user).order_by('-id')]
        cart_items = [{
            'id': oi.id,
            'product_title': oi.product_title,
            'qty': oi.qty,
            'unit_price': oi.price,
            'status': oi.get_status_display(),
            'image_URL': oi.get_cover_image(),
            'total_price': oi.total_price,
        } for oi in OrderItem.objects.filter(user=user, status=OrderItem.OrderItemStatus.INCART).order_by('-id')]
        wishlisted_items = [{
            'id': oi.id,
            'product_title': oi.product_title,
            'qty': oi.qty,
            'unit_price': oi.price,
            'status': oi.get_status_display(),
            'image_URL': oi.get_cover_image(),
            'total_price': oi.total_price,
        } for oi in OrderItem.objects.filter(user=user, status=OrderItem.OrderItemStatus.WISHLIST).order_by('-id')]

        user_data = {
            'id': user.id,
            'name': user.get_full_name(),
            'email': user.email,
            'mobile': user.mobile,
            'is_active': user.is_active,
            'is_admin': user.is_superuser,
            'orders': order_ids,
            'cart_items': cart_items,
            'wishlisted_items': wishlisted_items,
        }
        response_data['user'] = user_data

        return Response(response_data, status=status.HTTP_202_ACCEPTED)
