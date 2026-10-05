from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsCustomer

from .models import CartItem
from .serializers import (
    AddToCartSerializer,
    CartSerializer,
    UpdateCartItemSerializer,
)
from .services import add_to_cart, get_cart, update_cart_item


class CartBaseView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]


class CartView(CartBaseView):
    @extend_schema(responses=CartSerializer)
    def get(self, request):
        return Response(CartSerializer(get_cart(request.user)).data)


class CartClearView(CartBaseView):
    @extend_schema(responses={204: None})
    def delete(self, request):
        cart = get_cart(request.user)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemCreateView(CartBaseView):
    @extend_schema(request=AddToCartSerializer, responses={201: CartSerializer})
    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = add_to_cart(request.user, **serializer.validated_data)
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(CartBaseView):
    """فقط آیتم‌های سبدِ خودِ کاربر قابل دسترسی‌اند (در غیر این صورت 404)."""

    def get_item(self, request, pk):
        return get_object_or_404(
            CartItem.objects.select_related("product__category", "cart__user"),
            pk=pk,
            cart__user=request.user,
        )

    @extend_schema(request=UpdateCartItemSerializer, responses=CartSerializer)
    def patch(self, request, pk):
        item = self.get_item(request, pk)
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = update_cart_item(item, **serializer.validated_data)
        return Response(CartSerializer(cart).data)

    @extend_schema(responses=CartSerializer)
    def delete(self, request, pk):
        self.get_item(request, pk).delete()
        return Response(CartSerializer(get_cart(request.user)).data)
