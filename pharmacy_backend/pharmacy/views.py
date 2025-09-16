from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .models import Category, Product, Order
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        items = order.items.all()
        item_details = "\n".join([f"{item.quantity} x {item.product.name} - ${item.price}" for item in items])

        send_mail(
            subject=f'Order Confirmation - Order {order.unique_order_id}',
            message=(
                f"Thank you for your order!\n\n"
                f"Order ID: {order.unique_order_id}\n"
                f"Total: ${order.total_price}\n"
                f"Shipping Address: {order.shipping_address}\n\n"
                f"Items:\n{item_details}\n\n"
                f"We will process your order soon."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )

        send_mail(
            subject=f'New Order Notification - Order {order.unique_order_id}',
            message=(
                f"A new order has been placed.\n\n"
                f"Order ID: {order.unique_order_id}\n"
                f"Customer Email: {order.email}\n"
                f"Total: ${order.total_price}\n"
                f"Shipping Address: {order.shipping_address}\n\n"
                f"Items:\n{item_details}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)