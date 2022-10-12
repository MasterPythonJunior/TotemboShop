from django import template
from store.models import Category, FavouriteProducts

register = template.Library()

@register.simple_tag()
def get_categories():
    categories = Category.objects.all()
    return categories


@register.simple_tag()
def get_sorted():
    sorters = [
        {
            'title': 'По цене',
            'sorters': [
                ['price', 'По возрастанию'],
                ['-price', 'По убыванию']
            ]
        },
        {
            'title': 'По цвету/материалу',
            'sorters': [
                ['colour', 'От А до Я'],
                ['-colour', 'От Я до А']
            ]
        },
        {
            'title': 'По размеру',
            'sorters': [
                ['size', 'По возрастанию'],
                ['-size', 'По убыванию']
            ]
        },
        {
            'title': 'По названию',
            'sorters': [
                ['title', 'От А до Я'],
                ['-title', 'От Я до А']
            ]
        }
    ]
    return sorters


@register.simple_tag()
def get_favourite_products(user):
    favs = FavouriteProducts.objects.filter(user=user)
    products = [i.product for i in favs]
    return products

