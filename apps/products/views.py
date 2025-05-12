from django.db.models import Max
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, viewsets
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny
)
from rest_framework.views import APIView
from .models import Product, Order
from .serializers import ProductSerializer, ProductInfoSerializer, OrderSerializer, OrderCreateSerializer
from .filters import ProductFilter, InStockFilterBackend, OrderFilter

class ProductListCreateApiView(generics.ListCreateAPIView):
    queryset = Product.objects.order_by('-created_at')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend
    ]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'stock']
    pagination_class = LimitOffsetPagination

    @method_decorator(cache_page(timeout=60 * 15, key_prefix='product_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'product_id'

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
class ProductInfoAPIView(APIView):
    serializer_class = ProductInfoSerializer

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products,
            'count': len(products),
            'max_price': products.aggregate(max_price=Max('price'))['max_price']
        })
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    @method_decorator(cache_page(timeout=60 * 15, key_prefix='order_list'))
    @method_decorator(vary_on_headers('Authorization'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

# class OrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related('items__product')
#     serializer_class = OrderSerializer


# class UserOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related('items__product')
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         qs = super().get_queryset()
#         return qs.filter(user=self.request.user)

