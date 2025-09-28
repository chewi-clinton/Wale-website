from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, OrderViewSet, ProductVariantViewSet, PrescriptionRequestViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'variants', ProductVariantViewSet)
router.register(r'prescription-request', PrescriptionRequestViewSet, basename='prescription-request')

urlpatterns = [
    path('', include(router.urls)),
    path('products/<int:product_id>/variants/', ProductVariantViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-variants'),
]