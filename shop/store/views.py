from django.shortcuts import render, redirect
from .models import Category, Product, Review, FavouriteProducts
from django.views.generic import ListView, DetailView
# Create your views here.
from django.contrib.auth import login, logout
from django.contrib import messages
from django.urls import reverse
from .forms import RegistrationForm, LoginForm, ReviewForm, CustomerForm, ShippingForm
from .utils import CartForAuthenticatedUser, get_cart_data
from shop import settings
import stripe


class ProductList(ListView):
    model = Product
    extra_context = {
        'title': 'TOTEMBO: Главная страница'
    }
    template_name = 'store/product_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        categories = Category.objects.all()
        data = []
        for category in categories:
            products = category.products.all()[:4]

            if category.image:
                image = category.image.url
            else:
                image = 'https://экологиякрыма.рф/img/19893719.jpg'

            data.append({
                'title': category,
                'products': products,
                'image': image
            })
        return data

class ProductListByCategory(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'store/category_detail.html'

    def get_queryset(self):
        sort_field = self.request.GET.get('sort')
        category = Category.objects.get(slug=self.kwargs['slug'])
        products = category.products.all()
        if sort_field:
            products = products.order_by(sort_field)
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        category = Category.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'Категория: {category.title}'
        return context


class ProductDetail(DetailView):  # product_detail.html
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'Товар - {product.title}'
        products = Product.objects.all()
        data = []
        for i in range(4):
            from random import randint
            random_index = randint(0, len(products) - 1)
            product = products[random_index]
            if product not in data:
                data.append(product)
        context['products'] = data
        context['reviews'] = Review.objects.filter(product__slug=self.kwargs['slug'])
        if self.request.user.is_authenticated:
            context['review_form'] = ReviewForm()
        return context

def login_registration(request):
    context = {
        'title': 'Войти или зарегестрироваться',
        'login_form': LoginForm(),
        'registration_form': RegistrationForm()
    }
    return render(request, 'store/login_registration.html', context)

def user_login(request):
    form = LoginForm(data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('product_list')
    else:
        messages.error(request, 'Не верное имя пользователя или пароль')
        return redirect('login_registration')


def user_logout(request):
    logout(request)
    return redirect('product_list')


def register(request):
    form = RegistrationForm(data=request.POST)
    if form.is_valid():
        user = form.save()
        messages.success(request, 'Аккаунт успешно создан. Войдите в аккаунт!')
    else:
        for error in form.errors:
            messages.error(request, form.errors[error][0])
    return redirect('login_registration')


def save_review(request, product_slug):
    form = ReviewForm(data=request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.author = request.user
        product = Product.objects.get(slug=product_slug)
        review.product = product
        review.save()
    return redirect('product', product_slug)


def save_or_delete_fav(request, product__slug):
    user = request.user if request.user.is_authenticated else None
    product = Product.objects.get(slug=product__slug)
    if user:
        favs = FavouriteProducts.objects.filter(user=user)
        if product in [i.product for i in favs]:
            fav_product = FavouriteProducts.objects.get(user=user, product=product)
            fav_product.delete()
        else:
            FavouriteProducts.objects.create(user=user, product=product)
    next_page = request.META.get('HTTP_REFERER', 'product_list')
    return redirect(next_page)


class FavouriteProductsView(ListView):
    model = FavouriteProducts
    context_object_name = 'products'
    template_name = 'store/favourite_products.html'

    def get_queryset(self):
        user = self.request.user
        favs = FavouriteProducts.objects.filter(user=user)
        products = [i.product for i in favs]
        return products


def cart(request):
    cart_info = get_cart_data(request)
    context = {
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'order': cart_info['order'],
        'products': cart_info['products']
    }
    return render(request, 'store/cart.html', context)


def to_cart(request, product_id, action):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request, product_id, action)
        return redirect('cart')
    else:
        return redirect('login_registration')


def checkout(request):
    cart_info = get_cart_data(request)
    context = {
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'order': cart_info['order'],
        'items': cart_info['products'],
        'title': 'Сделать заказ',
        'customer_form': CustomerForm(),
        'shipping_form': ShippingForm()
    }
    return render(request, 'store/checkout.html', context)



def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()
        total_price = cart_info['cart_total_price']
        total_quantity = cart_info['cart_total_quantity']
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Товары с TOTEMBO'
                        },
                        'unit_amount': int(total_price * 100)
                    },
                    'quantity': total_quantity
                }
            ],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('successPayment')),
            cancel_url=request.build_absolute_uri(reverse('successPayment'))
        )
        return redirect(session.url, 303)


def successPayment(request):
    user_cart = CartForAuthenticatedUser(request)
    user_cart.clear()
    messages.success(request, 'Оплата прошла успешно!')
    return render(request, 'store/success.html')