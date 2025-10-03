from django.contrib import admin
from .models import Category, Product, ProductVariant, Order, OrderItem

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 5
    min_num = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_popular']  # ADDED: is_popular
    list_filter = ['category', 'is_popular']  # ADDED: is_popular
    search_fields = ['name', 'description']
    inlines = [ProductVariantInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'description', 'image')
        }),
        ('Popularity', {  # ADDED: Popularity section
            'fields': ('is_popular',)
        }),
    )

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'price', 'stock']
    list_filter = ['product']
    search_fields = ['product__name', 'name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'variant', 'quantity', 'price']
    search_fields = ['product__name', 'variant__name']