from django.urls import path
from .import views

urlpatterns = [
    path('',views.home,name='home'),
    path('home/',views.home,name='home'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('faq/',views.faq,name='faq'),
    path('search/',views.search,name='search'),
    path('shop/', views.shop, name="shop"),
    path('products/<int:id>/', views.single_product, name="product"),
    path('profile/',views.profile,name="profile"),
    path('login/',views.loginView,name="login"),
    path('logout/',views.logoutView,name="logout"),
    path('register/',views.register,name="register"),
    path("cart_add/<int:pk>", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart, name="cart"),
    path("cart_update/", views.cart_update, name="cart_update"),
    path('delete/<int:pk>',views.product_delete,name="cart_delete"),
    path('checkout/',views.checkout,name="checkout"),
    path('verify-payment/<str:reference>/', views.verify_payment, name="verify_payment"),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name="order_confirmation"),
    # path('add_comment/<int:id>/', views.add_comment, name="add_comment")
]