from django.db.models import Q
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

#def home(request):
# return render(request, 'app/home.html') 

class ProductView(View):
    def get(self, request):
        totalitem = 0
        topwears = Product.objects.filter(category='ST')
        bottomwears = Product.objects.filter(category='JT')
        mobiles = Product.objects.filter(category='M')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/home.html', {'topwears':topwears, 'bottomwears':bottomwears, 'mobiles':mobiles, 'totalitem':totalitem})

#------------------------------------------------------------------------------------


#def product_detail(request, pk):   
# return render(request, 'app/productdetail.html')

class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        totalitem = 0
        item_already_exist = False
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            item_already_exist = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        return render(request, 'app/productdetail.html', {'product':product, 'item_already_exist': item_already_exist, 'totalitem':totalitem})

#-------------------------------------------------------------------------------------

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('p_id')
    product = Product.objects.get(id=product_id) 
    cart = Cart(user=user, product=product)
    cart.save()
    return redirect('/cart')

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        #print(cart) //gives queryset object
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        #print(cart_product) //[<Cart: 1>, <Cart: 2>] 
        if cart_product:
            for p in cart_product:
                final_price = p.product.selling_price - p.product.discounted_price
                #print(final_price)
                tempamount = (p.quantity * final_price)
                amount += tempamount
                #print(amount)
                totalamount = amount + shipping_amount
            return render(request, 'app/addtocart.html', {'carts':cart, 'totalamount':totalamount, 'shipping_amount':shipping_amount, 'amount':amount, 'final_price':final_price})    
        else:
            return render(request, 'app/emptycart.html')


def plus_cart(request):
    if request.method == 'GET':
        product_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=product_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        amount = 0.0
        shipping_amount =70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        if cart_product:
            for p in cart_product:
                final_price = p.product.selling_price - p.product.discounted_price
                tempamount = (p.quantity * final_price)
                amount += tempamount

            data = {
                'quantity': c.quantity,
                'amount': amount, 
                'totalamount': amount + shipping_amount
            }
            return JsonResponse(data)


def minus_cart(request):
    if request.method == 'GET':
        product_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=product_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        amount = 0.0
        shipping_amount =70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        if cart_product:
            for p in cart_product:
                final_price = p.product.selling_price - p.product.discounted_price
                tempamount = (p.quantity * final_price)
                amount += tempamount

            data = {
                'quantity': c.quantity,
                'amount': amount, 
                'totalamount': amount + shipping_amount
            }
            return JsonResponse(data)


def remove_cart(request):
    if request.method == 'GET':
        product_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=product_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount =70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        if cart_product:
            for p in cart_product:
                final_price = p.product.selling_price - p.product.discounted_price
                tempamount = (p.quantity * final_price)
                amount += tempamount

            data = {
                'amount': amount, 
                'totalamount': amount + shipping_amount
            }
            return JsonResponse(data)


#-------------------------------------------------------------------------------------


def buy_now(request): 
 return render(request, 'app/buynow.html')  

#-------------------------------------------------------------------------------------


#def profile(request): 
# return render(request, 'app/profile.html')

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        totalitem = 0
        form = CustomerProfileForm()
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/profile.html', {'form':form, 'active': 'btn-primary', 'totalitem':totalitem})
        
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=user, name=name, locality=locality, city=city, state=state, zipcode=zipcode)    
            reg.save()
            messages.success(request, 'Congrats!! Your Profile is Updated :)')
        return render(request, 'app/profile.html', {'form':form, 'active': 'btn-primary'})

#-------------------------------------------------------------------------------------

@login_required
def address(request):
    addr = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'addr':addr, 'active':'btn-primary'})

#-------------------------------------------------------------------------------------

@login_required
def orders(request):
    ordp = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'order_placed':ordp})

#-------------------------------------------------------------------------------------


#def change_password(request):
# return render(request, 'app/changepassword.html')

#-------------------------------------------------------------------------------------


def mobile(request, data=None):
    if request.method == 'GET':
        totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))    

    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'Oppo' or data == 'Samsung':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'below':
        mobiles = Product.objects.filter(category='M').filter(selling_price__lt=1000)
    elif data == 'above':
        mobiles = Product.objects.filter(category='M').filter(selling_price__gt=1000)            
    return render(request, 'app/mobile.html', {'mobiles':mobiles, 'totalitem':totalitem})

def laptop(request, data=None):
    if request.method == 'GET':
        totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))    
    if data == None:
        laptops = Product.objects.filter(category='L')
    elif data == 'Dell' or data == 'Lenovo':
        laptops = Product.objects.filter(category='L').filter(brand=data)       
    return render(request, 'app/laptop.html', {'laptops':laptops, 'totalitem':totalitem})

def shoes(request, data=None):
    if request.method == 'GET':
        totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))    

    if data == None:
        shoe = Product.objects.filter(category='S')
    elif data == 'Sneakers' or data == 'Adidas':
        shoe = Product.objects.filter(category='S').filter(brand=data)       
    return render(request, 'app/shoes.html', {'shoe':shoe, 'totalitem':totalitem})

def watch(request, data=None):
    if request.method == 'GET':
        totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))    

    if data == None:
        wat = Product.objects.filter(category='W')
    elif data == 'Fastrack' or data == 'Puma':
        wat = Product.objects.filter(category='W').filter(brand=data)       
    return render(request, 'app/watches.html', {'wat':wat, 'totalitem':totalitem})    

#---------------------------------------------------------------------------------------


#def login(request):
# return render(request, 'app/login.html')

#-----------------------------------------------------------------------------


#def customerregistration(request):
# return render(request, 'app/customerregistration.html')

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form':form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Congrats!! Registered Successfully :)')
            form.save()
        return render(request, 'app/customerregistration.html', {'form':form}) 

#------------------------------------------------------------------------------------

@login_required
def checkout(request):
    if request.method == 'GET':
        totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))    
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    total_amount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    #print(cart_product) //[<Cart: 1>, <Cart: 2>] 
    if cart_product:
        for p in cart_product:
            final_price = p.product.selling_price - p.product.discounted_price
            tempamount = (p.quantity * final_price)
            amount += tempamount
        totalamount = amount + shipping_amount
    return render(request, 'app/checkout.html', {'add':add, 'cart_items':cart_items , 'totalamount':totalamount, 'totalitem':totalitem})

@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart_items = Cart.objects.filter(user=user)
    for c in cart_items:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect('orders')