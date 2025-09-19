# pharmacy/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from django.core.mail import send_mail
from django.conf import settings
from .models import Category, Product, Order
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAdminUser]
        return super(CategoryViewSet, self).get_permissions()

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAdminUser]
        return super(ProductViewSet, self).get_permissions()

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    lookup_field = 'unique_order_id'  # Use unique_order_id instead of id for lookups

    def get_permissions(self):
        if self.action in ['create', 'retrieve']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAdminUser]
        return super(OrderViewSet, self).get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

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