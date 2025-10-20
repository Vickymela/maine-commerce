from itertools import product
from django.contrib import admin
from . models import *
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_type','product_name','current_price')
    search_fields = ('product_type','product_name',)
    list_filter =  ('product_type','product_name',)

admin.site.register(Product,ProductAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Category,CategoryAdmin)


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name','email','subject')
    search_fields = ('name','subject')
    list_filter = ('name','subject')

admin.site.register(Contact,ContactAdmin)
    

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    search_fields = ('username', 'email')
    
admin.site.register(CustomUser, CustomUserAdmin)

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user',)
    list_filter = ('created_at',)

admin.site.register(Cart, CartAdmin)

admin.site.register(Payment)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Comment)