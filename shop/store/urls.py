from django.urls import path
from .views import *

urlpatterns = [
    path('', ProductList.as_view(), name='product_list'),
    path('category/<slug:slug>/', ProductListByCategory.as_view(), name='category'),
    path('product/<slug:slug>/', ProductDetail.as_view(), name='product'),
    path('login_registration/', login_registration, name='login_registration'),
    path('login', user_login, name='login'),
    path('logout', user_logout, name='logout'),
    path('register', register, name='register'),
    path('save_review/<slug:product_slug>', save_review, name='save_review'),
    path('add-or-delete/<slug:product__slug>/', save_or_delete_fav, name='save_or_del'),
    path('favourite/', FavouriteProductsView.as_view(), name='favourite'),
    path('cart/', cart, name='cart'),
    path('to_cart/<int:product_id>/<str:action>/', to_cart, name='to_cart'),
    path('checkout', checkout, name='checkout'),

    path('payment/', create_checkout_session, name='payment'),
    path('payment-success/', successPayment, name='successPayment')
]