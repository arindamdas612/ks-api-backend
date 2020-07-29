from .models import Order


def get_diplay_id_seq():
    last_order = Order.objects.all().order_by('id').last()
    time_string = datetime.now().strftime("%y%m%d")
    if not last_invoice:
        return f'ORD{time_string}00001'
    order_no = last_order.display_id
    order_int = int(order_no[-5:])
    width = 5
    new_invoice_int = invoice_int + 1
    formatted = (width - len(str(new_invoice_int))) * \
        "0" + str(new_invoice_int)
    new_order_no = 'ORD' + time_string + str(formatted)
    return new_order_no
