from email import message
from tkinter import CASCADE
from django.db import models 
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.fields import related


# Create your models here.
class CustomUser(AbstractUser):
    # this has all the user table fields plus whichever field swe enter here
    #email unique true means user cannot have the same email field whewe enter email from our default User
    phone_Number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

class UserProfile(models.Model):
    user  = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to="profile/")

    def __str__(self):
        return self.user.username
    




class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name




class Product(models.Model):
    product_type = models.ForeignKey(Category, on_delete= models.CASCADE)
    product_name = models.CharField(max_length=250)
    current_price = models.DecimalField(max_digits=10,decimal_places=2)
    previous_price = models.DecimalField(max_digits=10,decimal_places=2)
    description = models.TextField()
    image = models.ImageField( upload_to='product/' )
    image2= models.ImageField( upload_to='product/')
    date_posted = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    sku = models.CharField(max_length=50,null=True,blank=True)
    date_added= models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name




class Contact(models.Model):
    name = models.CharField( max_length=50)
    email = models.EmailField( max_length=254)
    subject = models.CharField(max_length=450)
    message = models.TextField()

    def __str__(self):
        return self.name + " " + self.subject

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s cart"
    
    @property
    def subtotal(self):

        # list = []

        # for item in self.item.all():
        #     list.append(item)

        # total = sum(list)

        return sum(item.total for item in self.item.all())
    

    
    @property
    def total(self):
        return self.subtotal + 70
    
        
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="item")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.cart.user}'s cart"
    
    @property
    def total(self):
        return self.product.current_price * self.quantity
    

class Order(models.Model):
    user = models.ForeignKey( settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="orders")
    first_name = models.CharField( max_length=50, null= True)
    last_name = models.CharField( max_length=50, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=50 ,null=True)
    country = models.CharField( max_length=50 ,null=True)
    state = models.CharField( max_length=50 ,null=True)
    town = models.CharField( max_length=50 ,null=True)
    post_code = models.CharField(max_length=50,null=True)
    address = models.CharField(max_length=50,null=True)
    apartment = models.CharField( max_length=50,null=True)
    company = models.CharField( max_length=50,null=True)
    status = models.CharField( 

            max_length = 20,
            choices =[
                ("pending","Pending"),
                ("paid","paid"),
                ("shipped","Shipped"),
                ("completed","Completed"),
            ],
            default = "pending"
    )
    notes = models.TextField(blank=True,null=True)
    total = models.DecimalField( max_digits=10, decimal_places=2,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order,related_name = "items",on_delete=models.CASCADE)
    product = models.CharField( max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product} x {self.quantity}"



class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE,related_name="payment")
    email = models.EmailField()
    amount = models.PositiveIntegerField()
    refrence= models.CharField(max_length=50)
    verified = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order} - {self.refrence}"
    
class Comment(models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name= models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    Comment = models.TextField()

    def __str__(self):
        return self.user.username