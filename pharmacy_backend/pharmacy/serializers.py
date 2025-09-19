from rest_framework import serializers
from .models import Category, Product, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image = serializers.ImageField(use_url=True, allow_null=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'category_name', 'description', 'price', 'old_price', 'stock', 'image']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'unique_order_id', 'email', 'shipping_address', 
            'total_price', 'payment_method', 'status', 'created_at', 'items'
        ]
        read_only_fields = ['id', 'unique_order_id', 'created_at', 'status']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        request = self.context.get('request')
        user = None
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        
        order = Order.objects.create(
            user=user,
            **validated_data
        )
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order