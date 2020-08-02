from .models import Order, OrderItem, OrderStatus, OrderActivity


def get_update_order_by_id(order_id):
    order = Order.objects.get(pk=order_id)

    order_item_data = []
    order_activity_data = [{
        'id': -1,
        'prev_status': 'Unavailable',
        'next_status': 'Placed',
        'activity_dt': order.created_on.isoformat(),
        'user': order.user.get_full_name(),
        'is_admin': order.user.is_superuser,
    }]
    order_value = 0.0
    order_items = OrderItem.objects.filter(linked_order__id=order.id)
    order_activities = OrderActivity.objects.filter(order__id=order.id)
    for oi in order_items:
        if oi.status != OrderItem.OrderItemStatus.CANCELLED and oi.status != OrderItem.OrderItemStatus.NOSTOCK:
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
    return ord


def get_updated_order_data():
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
        order_value = 0.0
        order_items = OrderItem.objects.filter(linked_order__id=order.id)
        order_activities = OrderActivity.objects.filter(order__id=order.id)
        for oi in order_items:
            if oi.status != OrderItem.OrderItemStatus.CANCELLED and oi.status != OrderItem.OrderItemStatus.NOSTOCK:
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

    return order_data


def process_order_action(next_status, order_id, user):
    process_code = 0
    process_message = ''
    order_item_data = []
    order = Order.objects.get(pk=order_id)
    order_activity_data = [{
        'id': -1,
        'prev_status': 'Unavailable',
        'next_status': 'Placed',
        'activity_dt': order.created_on.isoformat(),
        'user': order.user.get_full_name(),
        'is_admin': order.user.is_superuser,
    }]

    prev_status = order.get_status_display()
    no_error = True
    order_items = None
    action_processed = False

    if next_status == 'Acknowledged':
        items_status_ordered = True
        action_processed = True
        order_items = OrderItem.objects.filter(
            linked_order=order)
        for order_item in order_items:
            if order_item.status != OrderItem.OrderItemStatus.ORDERED and order_item.status != OrderItem.OrderItemStatus.NOSTOCK:
                items_status_ordered = False

        if not items_status_ordered:
            no_error = False
            process_message = 'Not all Order Items are available. Change the order status to No Stock (P)'
        else:
            order.status = OrderStatus.ACKNOWLEDGED
            for order_item in order_items:
                if order_item.should_change_status():
                    order_item.status = OrderItem.OrderItemStatus.INPROCESS
                    order_item.save()
            order.save()
            process_message = 'Order Acknowledged'

    if next_status == 'Ready':
        action_processed = True
        order_items = OrderItem.objects.filter(
            linked_order=order)
        order.status = OrderStatus.READY
        order.save()
        process_message = 'Order Ready'

    if next_status == 'In Transit':
        action_processed = True
        order_items = OrderItem.objects.filter(
            linked_order=order)
        order.status = OrderStatus.IN_TRANSIT
        order.save()
        process_message = 'Order In Transit'

    if next_status == 'Delivered':
        action_processed = True
        order_items = OrderItem.objects.filter(
            linked_order=order)
        order.status = OrderStatus.DELIVERED
        for order_item in order_items:
            if order_item.should_change_status():
                order_item.status = OrderItem.OrderItemStatus.DELIVERED
                order_item.save()
        order.save()
        process_message = 'Order Delivered (Completed)'

    if next_status == 'Dismissed':
        action_processed = True
        order_items = OrderItem.objects.filter(
            linked_order=order)
        order.status = OrderStatus.DISMISSED
        for order_item in order_items:
            if order_item.should_change_status():
                order_item.status = OrderItem.OrderItemStatus.CANCELLED
                order_item.save()
        order.save()
        process_message = 'Order Dismissed (Completed)'

    if next_status == 'No Stock (P)':
        action_processed = True
        order_items = OrderItem.objects.filter(linked_order=order)
        item_count = 0
        partial_nostock_count = 0
        for order_item in order_items:
            item_count = item_count + 1
            if order_item.status == OrderItem.OrderItemStatus.NOSTOCK:
                partial_nostock_count = partial_nostock_count + 1

        if partial_nostock_count == 0:
            process_code = 1
            process_message = 'No order items marked "No Stock", could not modify the Order'
            no_error = False

        elif partial_nostock_count == item_count and item_count == 1:
            process_code = 1
            process_message = 'Contains only one Order Item, Try the "No Stock" Action'
            no_error = False

        elif partial_nostock_count == item_count:
            process_code = 1
            process_message = 'All orders items are marked "No Stock", Try the "No Stock" Action'
            no_error = False
        else:
            order.status = OrderStatus.PARTIAL_NOSTOCK
            order_items = OrderItem.objects.filter(linked_order=order)
            for order_item in order_items:
                if order_item.status != OrderItem.OrderItemStatus.NOSTOCK:
                    order_item.status = OrderItem.OrderItemStatus.INPROCESS
                    order_item.save()
            order.save()
            process_message = 'Order partially marked as "No Stock"'

    if next_status == 'No Stock':
        action_processed = True
        order_items = OrderItem.objects.filter(
            linked_order=order)
        order.status = OrderStatus.NOSTOCK
        for order_item in order_items:
            if order_item.should_change_status():
                order_item.status = OrderItem.OrderItemStatus.NOSTOCK
                order_item.save()
        order.save()
        process_message = 'Order marked as "No Stock"'

    if not action_processed:
        process_code = 1
        process_message = 'Action Unknown'

    if no_error:
        order_items = OrderItem.objects.filter(linked_order=order)
        order_activity = OrderActivity(
            order=order, prev_status=prev_status, next_status=next_status, changed_by=user)
        order_activity.save()
        order_value = 0
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

        for ord_act in OrderActivity.objects.filter(order__id=order.id):
            act = {
                'id': ord_act.id,
                'prev_status': ord_act.prev_status,
                'next_status': ord_act.next_status,
                'activity_dt': ord_act.changed_on.isoformat(),
                'user': ord_act.changed_by.get_full_name(),
                'is_admin': ord_act.changed_by.is_superuser,
            }
            order_activity_data.append(act)

    action_list = order.next_actions()
    return_data = [process_code, process_message,
                   order_item_data, action_list, order_activity_data]

    return return_data
