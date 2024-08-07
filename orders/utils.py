import datetime

def generate_order_number(pk):
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%S')
    print("current_datetime: "+current_datetime)
    order_number = current_datetime + str(pk)
    print("order_number: "+order_number)
    return order_number