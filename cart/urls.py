from django.urls import path

from .views import CartClearView, CartItemCreateView, CartItemDetailView, CartView

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path("clear/", CartClearView.as_view(), name="cart-clear"),
    path("items/", CartItemCreateView.as_view(), name="cart-item-add"),
    path("items/<int:pk>/", CartItemDetailView.as_view(), name="cart-item-detail"),
]
