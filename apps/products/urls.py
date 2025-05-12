from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path('products/', views.ProductListCreateApiView.as_view()),
    path('products/info/', views.ProductInfoAPIView.as_view()),
    path('products/<int:product_id>/', views.ProductDetailAPIView.as_view()),
]

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet)

urlpatterns += router.urls
