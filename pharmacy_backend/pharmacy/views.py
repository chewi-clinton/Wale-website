from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import logging
from .models import Category, Product, Order, ProductVariant
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer, ProductVariantSerializer

logger = logging.getLogger(__name__)

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAdminUser]
        return super(ProductVariantViewSet, self).get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.kwargs.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        elif 'product_id' in self.request.query_params:
            product_id = self.request.query_params.get('product_id')
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        product_id = self.kwargs.get('product_id')
        if product_id:
            context['product_id'] = product_id
        return context

    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        if product_id:
            serializer.save(product_id=product_id)
        else:
            serializer.save()

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    lookup_field = 'unique_order_id' 

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
        
        context = {
            'order_id': order.unique_order_id,
            'date': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'email': order.email,
            'shipping_address': order.shipping_address,
            'payment_method': order.payment_method,
            'total_price': order.total_price,
            'items': [
                {
                    'name': item.product.name,
                    'variant': item.variant.name,
                    'quantity': item.quantity,
                    'price': item.price,
                    'total': item.price * item.quantity
                } for item in items
            ],
            'customer_name': f"{order.user.first_name} {order.user.last_name}" if order.user else "Guest",
            'phone': getattr(order.user, 'phone', 'Not provided'),
            'year': order.created_at.year
        }
        
        try:
            customer_html = render_to_string('email/order_confirmation.html', context)
            send_mail(
                subject=f'Order Confirmation - Order {order.unique_order_id}',
                message=f'Thank you for your order! Your order ID is {order.unique_order_id}.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.email],
                fail_silently=False,
                html_message=customer_html
            )
            logger.info(f"Customer confirmation email sent to {order.email} for order {order.unique_order_id}")
        except Exception as e:
            logger.error(f"Failed to send customer email for order {order.unique_order_id}: {str(e)}")
        
        try:
            admin_html = render_to_string('email/admin_notification.html', context)
            send_mail(
                subject=f'New Order Notification - Order {order.unique_order_id}',
                message=f'New order received: {order.unique_order_id}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
                html_message=admin_html
            )
            logger.info(f"Admin notification email sent for order {order.unique_order_id}")
        except Exception as e:
            logger.error(f"Failed to send admin email for order {order.unique_order_id}: {str(e)}")
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)