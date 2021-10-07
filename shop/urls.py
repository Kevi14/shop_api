from rest_framework import routers
from . import views
from django.urls import path

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'decks', views.DecksViewSet, basename='decks')
router.register(r'images', views.ProductImagesViewSet, basename='image')
router.register(r'orders', views.OrdersViewSet, basename='orders')
router.register(r'items_ordered', views.ItemsOrderedViewSet, basename='items_ordered')

urlpatterns = [
    path('products/<slug:category_slug>/<slug:product_slug>/', views.DecksViewSet.as_view({'get':'list'})),
    path('paypal_payment',views.CreatePayLink.as_view()),
    path('capture_payment/',views.CapturePay.as_view()),
    path('register_order/',views.RegisterOrder.as_view())
]


urlpatterns += router.urls