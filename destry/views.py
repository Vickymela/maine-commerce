from django.contrib import messages
from django.db.models.fields import json
from django.http import response
from django.shortcuts import get_object_or_404, render
from .models import *
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User
from django.conf import settings
import uuid
import requests

# Create your views here.
def home(request):
    products = Product.objects.filter(is_active = True).order_by('-date_posted')
    context ={
        'products':products
    }

    return render(request,'crosscheck_index.html',context)

def about(request):
    return render(request,'about.html')

def contact(request):
    if request.method == 'POST':
        form = request.POST

        name = form.get('name')
        email = form.get('email')
        subject= form.get('subject')
        message = form.get('message')

        Contact.objects.create(
            name = name,
            email=email,
            subject=subject,
            message=message,
        )

        messages.success(request,'thank you for contacting us')
        return redirect('contact')


    
    return render(request,'contact.html')

def faq(request):
    return render(request,'faq.html')

def search(request):
    query = request.GET.get('q')
    result = []
    if query:
        result = Product.objects.filter(product_name__icontains = query, is_active = True)
    context = {
        'results':result,
        'query': query
    }

    return render(request,'search_results.html',context)

def shop(request):

    products = Product.objects.filter(is_active = True)

    context = {
        'products' : products
    }

    return render(request, 'shop-grid.html', context)


def single_product(request, id):

    product = Product.objects.get(id = id)

    context = {
        "product" : product
    }

    return render(request, "single-product.html", context)

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = get_user_model()

    currentUser = user.objects.get(username = request.user.username)

    if request.method == "POST":
        form = request.POST

        username = form.get("uname")
        firstname = form.get("fname")
        lastname = form.get("lname")
        email = form.get("email")
        phone = form.get("phone")
        password = form.get("password")
        cpassword = form.get("cpassword")

        currentUser.first_name = firstname
        currentUser.last_name = lastname
        currentUser.email = email

        if password == cpassword and password != "":
            currentUser.password = password

        user_with_username = None

        user_with_username = user.objects.filter(username = username).exists()



        if currentUser.username == username:
            pass
        else:
            if user_with_username != None:
                currentUser.username = username
            else:
                messages.error(request, "Username is already taken")




        currentUser.save()


    

    context =  {
        "user" : currentUser
    }

    return render(request,'my-account.html', context)

def add_to_cart(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')


    cart, _ =  Cart.objects.get_or_create(user = request.user)

    product = Product.objects.get(pk = pk)

    item, created = CartItem.objects.get_or_create(cart = cart, product = product)

    # if CartItem.objects.filter(cart=cart, product=product).exists():
    #     item = CartItem.objects.get(cart = cart, product = product)
    #     item.quantity += 1
    #     item.save()
    # else:
    #     cart_item = CartItem.objects.create(cart = cart, product = product)

    if not created:
        item.quantity += 1
        item.save()

    return redirect("cart")

def cart(request):
    if not request.user.is_authenticated:
      return redirect('login')

    cart, _ = Cart.objects.get_or_create(user = request.user)
    

    #the explaination of the code above
    """
    
        cart = None
        created = None

        if Cart.objects.filter(user = request.user).exists():
            cart = Cart.objects.get(user = request.user)
            created = False

        else:
            newCart = cart.objects.create(user = request.user)
            created = True
            cart = newCart

    
    """

    # for item  in cart.item.all:


    context = {
        "cart": cart,
    }

    return render(request,'cart.html', context)

def cart_update(request):
    if request.method == "POST":
        form = request.POST

        cart = Cart.objects.get(user = request.user)

        for item in cart.item.all():
            field_name = f"quantity_{item.id}"

            # quantity_5 : 
            # quantity_3 : 

            if field_name in request.POST:
                new_qty = int(form.get(field_name))

                if new_qty > 0:
                    item.quantity = new_qty
                    item.save()

                else:
                    item.delete()

    return redirect("cart")


def product_delete(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    
    item = None
    item = CartItem.objects.get(pk=pk)

    if item != None:
        item.delete()
    return redirect("cart")

def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    cart = Cart.objects.get(user = request.user)
    cart_items = cart.item.all()
    # cart_items = CartItem.objects.filter(cart = cart)
    sub_total = 0
    sub = []
    for item in cart_items:
        sub.append(item.product.current_price * item.quantity)
    sub_total = sum(sub)

    total = sub_total + 70
    
    if request.method == 'POST':
        form = request.POST

        country = form.get('country')
        fname = form.get('first_name')
        lname = form.get('lastname')
        company = form.get('company')
        street = form.get('street')
        apartment = form.get('apartment')
        town = form.get('town')
        state= form.get('state')
        zipcode= form.get('zipcode')
        email= form.get('email')
        phone= form.get('phone')

        order = Order.objects.create(
            user = request.user,
            first_name =fname,
            last_name = lname,
            email = email,
            phone = phone,
            country = country,
            state= state,
            town = town,
            post_code = zipcode,
            address = street,
            apartment = apartment,
            company = company,
            total = total,
            )
        
        reference = str(uuid.uuid4()).replace("-","")#to generate  a 32 char random uuid for the payment
        payment=Payment.objects.create(
            order=order,
            email = email,
            amount = int(total *100),
            refrence=  reference,
            verified = False,
        )
        for item in cart_items:
            OrderItem.objects.create(
                order = order,
                product = item.product,
                quantity = item.quantity,
                price = item.product.current_price

            )

        cart_items.delete()

        #initialize payment
        url ="https://api.paystack.co/transaction/initialize"
        headers= {"Authorization":f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        data={
            "email":email,
            "amount":payment.amount,
            "reference": payment.refrence,
            "callback_url": request.build_absolute_uri(f"/verify-payment/{payment.refrence}/")  #WILL VERIFY LATER

        }
        #sends post request to the paystack from our variables
        response = requests.post(url,headers=headers,json=data)
        # .json() converts our data to dict 
        res_data= response.json()

        if res_data["status"]:#if statua == true
            # redirect to paystack paymnet page
            return redirect(res_data["data"]["authorization_url"])
        else:
            #handle errors
            messages.error(request,"payment could not be initialized . try again ")
            return redirect("checkout")
        
    context= {
        "user":request.user,
        "subtotal":sub_total,
        "total":total,
    }
    

    return render(request,'checkout.html',context)

def verify_payment(request,reference):
    #this refrence is gotten from model /database cause we created a refrence filed in the above function that has a uuid
    payment=get_object_or_404(Payment,refrence=reference)
    headers = {"Authorization":f"Bearer{settings.PAYSTACK_SECRET_KEY}"}
    response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}",headers=headers)
    res_data = response.json()

    if res_data["status"] and res_data["data"]["status"] == "success":
        #mark payment as verifed
        payment.verified = True
        payment.save()

        #UPDATE THE ORDER STATUS
        payment.order.status ="paid"
        payment.order.save()

        messages.success(request,"payment successful! your order is confirmed")
        return redirect("order_confirmation", order_id = payment.order.id)
    else:
        messages.error(request,"payment  verification failed try again")
        return redirect("checkout")

def order_confirmation(request,order_id):
    order = get_object_or_404(Order,id=order_id,user=request.user)
    order_items = order.item.all()  #related name for orderitem model
    context ={
        "order":order,
        "order_items":order_items
    }
    return render(request,"order_confirmation.html",context)






def loginView(request):

    if request.method == "POST":
        form = request.POST

        username = form.get("username")
        password = form.get("password")

        user = None

        user = authenticate(request, username = username, password = password)

        if user != None:
            login(request, user)
            return redirect("home")
        
        else:
            messages.error(request, "Error logging user in!!")
        

        
    
    return render(request,'login.html',)

def logoutView(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        logout(request)
        return redirect("home")
    return render(request,'logout.html')

def register(request):

    if request.method == "POST":
        form = request.POST

        username = form.get("username")
        first_name = form.get("fname")
        last_name = form.get("lname")
        email = form.get("email")
        phone_number = form.get("phone")
        password = form.get("password")

        # Check if the usename already exists

        if CustomUser.objects.filter(username = username).exists():
            messages.error(request, "Username already exists please choose another")
            return redirect("register")
        
        # Check iif the email already exists

        if CustomUser.objects.filter(email = email).exists():
            messages.error(request, "this email already exists, please try and login")
            return redirect("register")
        
        # create and save user

        user = get_user_model()

        newUser = user.objects.create_user(username = username, email = email, password= password, first_name = first_name, last_name = last_name, phone_Number = phone_number)

        messages.success(request, "Registeration successful, please login!!")
        return redirect("login")



    return render(request,'register.html')

# def add_comment(request, id):
#     # user = get_user_model()

#     # currentUser = user.objects.get(username = request.user.username)
#     product = Comment.objects.get(id = id)

#     # context = {
#     #     "product" : product
#     # }

#     if request.method == "POST":
#         form = request.POST


#         username = form.get('name')
#         email = form.get('email')
#         comment = form.get('comment')

       
         
#         newComment = Comment.objects.create(
#              username = username,
#              comment =comment,
#              email = email
#          )
        


#     return redirect('home')
