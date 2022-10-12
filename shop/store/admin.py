from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Category, Product, Gallery


# Register your models here.

class GalleryInline(admin.TabularInline):
    model = Gallery
    fk_name = 'product'
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['pk', 'title', 'get_products_count']
    list_display_links = ['pk', 'title']
    list_filter = ['title']
    prepopulated_fields = {'slug': ('title',)}

    def get_products_count(self, obj):
        if obj.products:
            return str(len(obj.products.all()))
        else:
            return '0'

class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'price', 'quantity', 'created_at', 'get_photo')
    list_display_links = ('pk', 'title')
    list_editable = ('price', 'quantity')
    inlines = [GalleryInline]
    prepopulated_fields = {'slug': ('title', )}

    def get_photo(self, obj):
        if obj.images:
            try:
                return mark_safe(f'<img src="{obj.images.first().photo.url}" width=75>')
            except:
                return '-'
        else:
            return '-'
    get_photo.short_description = 'Миниатюра'

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
