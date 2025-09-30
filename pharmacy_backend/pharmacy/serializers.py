# serializers.py
from rest_framework import serializers
from .models import Category, Product, ProductVariant, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'price', 'stock']
        read_only_fields = ['id']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image = serializers.ImageField(use_url=True, allow_null=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'category_name', 'description', 'image', 'variants']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['product', 'variant', 'quantity', 'price', 'product_name', 'variant_name']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'unique_order_id', 'email', 'phone', 'shipping_address', 
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
            variant = item_data['variant']
            quantity = item_data['quantity']
            
            if variant.stock < quantity:
                raise serializers.ValidationError(
                    f"Not enough stock for {variant.product.name} - {variant.name}. "
                    f"Available: {variant.stock}, Requested: {quantity}"
                )
            
            OrderItem.objects.create(
                order=order,
                product=variant.product,
                variant=variant,
                quantity=quantity,
                price=variant.price
            )
            
            variant.stock -= quantity
            variant.save()
        
        return order