import  datetime
from decimal import Decimal
from http import client
from multiprocessing import context, current_process
from unicodedata import decimal
from urllib import request, response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from store.models import OrderProduct
from store.models import Payment
from store.models import Order
from store.models import Address
from store.models import WishList
from store.models import Variation
from store.models import Category, SubCategory
from store.models import Section
from store.models import product,Variation
from store.models import Cart, CartItem,Review
from .models import Account
from .forms import AddressForm, EditProfileUser, RegistrationForm, VerifyForm,ReviewForm
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from .verify import send,check
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q
import requests
import razorpay
import json
import urllib
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
            user. phone_number =  phone_number
            request.session['phone_number'] = phone_number
            user.save()  
            send(form.cleaned_data.get('phone_number'))   
            return redirect('verify') 

    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request,'accounts/register.html',context) 

def verify_code(request):
    if request.method == 'POST':
        form = VerifyForm(request.POST)
        if form.is_valid():
            print('dfghj')
            code = form.cleaned_data.get('code')
            phone_number = request.session['phone_number']
            
            if check(phone_number, code):
                user = Account.objects.get(phone_number = phone_number)
                print('gbhn')
                user.is_active = True
                user.save()
                return redirect('login')
    else:
        form = VerifyForm()
    return render(request, 'accounts/verify.html', {'form': form})
   


# def register(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             phone_number = form.cleaned_data['phone_number']
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']
#             username = email.split('@')[0]
#             user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
#             user. phone_number =  phone_number
#             user.save()
#             #User Activation
#             current_site = get_current_site(request)
#             mail_subject = 'Please activate your account'
#             message = render_to_string('accounts/account_verification_email.html',{
#                 'user':user,
#                 'domain':current_site,
#                 'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
#                 'token' : default_token_generator.make_token(user),
#             })
#             to_email = email
#             send_email = EmailMessage(mail_subject,message,to=[to_email])
#             send_email.send()
#             #messages.success(request,'Thankyou for registering with us.We have sent a verification email to your email address[pvomassery@gmail.com].Please verify it.')
#             return redirect('/accounts/login/?command=verification&email='+email)
#     else:
#         form = RegistrationForm()
#     context = {
#         'form': form,
#     }
#     return render(request,'accounts/register.html',context) 

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
  
        account = Account.objects.filter(email=email,is_active=False).exists()    
      
        if  account:
            acco=Account.objects.get(email=email) 
            phone=acco.phone_number         
            send(phone)
            messages.info(request,'Account already exists with this email id,Verify the account by entering otp send to you email.')
            return redirect('verify')

        user = auth.authenticate(email=email, password=password)

        if user is not None:

            if user.is_superadmin:
                auth.login(request,user)
                return redirect('admin_table')
    
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get the cart items from the user and his product variations
                    cart_item = CartItem.objects.filter(user=user) 
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all() 
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    # product_variation = [1,2,3,4,6]
                    # ex_var_list = [4,3,6,5]
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)  
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:    
                pass    
            auth.login(request,user)
            messages.success(request,'You are now logged in')            
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                print(query)
               
                params = dict(x.split('=')for x in query.split('&'))
                if 'next' in params:
                    print('---')
                    nextPage= params['next']
                    print(nextPage)
                    return redirect(nextPage)
                
                
            except:
                return redirect('home')    
        else:
            messages.error(request,'Invalid login credentials!!')  
            return redirect('login')  
    
    else:
        return render(request,'accounts/login.html')
def home(request):
    products = product.objects.all().order_by('-id')[0:6]
    section1 = product.objects.filter(section__name = 'Trendy Products')
    section2 = product.objects.filter(section__name = 'Just Arrived')
    context = {
        'products': products,
        'section1': section1,
        'section2': section2,
    }
    return render(request,'accounts/home.html',context) 

       
   
@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You were logged out!')
    return redirect('home')

def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulations! Your account is activated.')    
        return redirect('login')
    else:
        messages.error(request,'Invalid avctivation link')  
        return redirect('register') 


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            #Resett password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

            messages.success(request,'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request,'Account does not exist')    
            return redirect('forgotPassword')
    return render(request,'accounts/forgotPassword.html')        

def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):  
        request.session['uid'] = uid
        messages.success(request,'Please reset your password')  
        return redirect('resetPassword')
    else:
        messages.error(request,'This link has been expired!')  
        return redirect('login')  

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset successfully')
            return redirect('login')

        else:
            messages.error(request,'Password do not match!')    
            return redirect('resetPassword')  
    else:           
        return render(request,'accounts/resetPassword.html')                                    

def shop(request):
    items = product.objects.all().order_by('-id')[0:12]
    paginator = Paginator(items,8)
    page = request.GET.get('page')
    paged_items = paginator.get_page(page)
    context = {
         'items': paged_items,
    }
    return render(request,'accounts/shop.html',context) 

def store(request,category_slug=None):
    categories = None
    subcategories = None

    if category_slug != None:
        categories = get_object_or_404(Category,slug=category_slug)
        subcategories = product.objects.filter(category = categories)
        paginator = Paginator(subcategories,3)
        page = request.GET.get('page')
        paged_subcategories = paginator.get_page(page)
        subcategory_count = subcategories.count()
        

    else:
        subcategories = product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(subcategories,3)
        page = request.GET.get('page')
        paged_subcategories = paginator.get_page(page)
        subcategory_count = subcategories.count()
    context = {
        'subcategories' : paged_subcategories,
        'subcategory_count' : subcategory_count,
        'categories' : categories,

    }    
    return render(request,'accounts/store.html',context)

def sub_categories(request,category_slug=None,subcategory_slug=None):
    categories = None
    subcategories = None
    prod = None

    if  category_slug != None:
        categories = get_object_or_404(Category,slug=category_slug)
        subcategories = product.objects.filter(category = categories)
        if subcategory_slug != None:
    
            subcategories = get_object_or_404(SubCategory,slug=subcategory_slug)
            prod = product.objects.filter(subCategory=subcategories)
            paginator = Paginator(prod,8)
            page = request.GET.get('page')
            paged_prod = paginator.get_page(page)
            product_count = prod.count()
    else:
        subcategories = product.objects.all().filter(is_available=True)
        prod = product.objects.all().filter('-id')        
        product_count = prod.count()  
    
    context = {
        
        'subcategories' : subcategories,
        'prod' : paged_prod,
        'product_count' : product_count, 
    }    
    return render(request,'accounts/sub_categories.html',context)
    
def product_detail(request,category_slug,subcategory_slug,pro_slug):
    discount=0
    try:
        single_product = product.objects.get(category__slug=category_slug,subCategory__slug=subcategory_slug,slug=pro_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), Product=single_product).exists()
        review = Review.objects.filter(Product_id=single_product.id)
        n = review.count()
        print(review)
        rate =0
        rating =0
        if review :
            for rev in review:
                print(rev.rating)
                if rev.rating:
                    rate += int(rev.rating)
                    print(rate)
            rating = int(rate/n)   

        if single_product.discount:
            discount = single_product.price-single_product.discount
    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'discount': discount,
        'review' : review,
        'n' : n ,
        'rating': rating,
    }     

    return render(request,'accounts/product_detail.html',context)


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request,product_id):
    current_user = request.user
    Product = product.objects.get(id=product_id)

    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(Product=Product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass    
            
        
        # try:    
        #     cart = Cart.objects.get(cart_id=_cart_id(request))
        # except Cart.DoesNotExist:
        #     cart = Cart.objects.create(
        #         cart_id = _cart_id(request)
        #     ) 
        # cart.save()   
        is_cart_item_exists = CartItem.objects.filter(Product=Product,user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(Product=Product,user=current_user) 
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all() 
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if  product_variation in ex_var_list:
                # increase cart_item quantity 
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(Product=Product,id=item_id) 
                item.quantity += 1 
                item.save()
            else:  
                cart_item = CartItem.objects.create(Product = Product, quantity = 1,  user = current_user)
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)  
                item.save()  

        else:
            cart_item = CartItem.objects.create(
                Product = Product,
                quantity = 1,
                user = current_user,
            ) 
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)  
            cart_item.save()  
        return redirect('cart')
        # if the user is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(Product=Product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                    print(product_variation)
                except:
                    pass    

            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id=_cart_id(request)) 

            cart.save()          

        is_cart_item_exists = CartItem.objects.filter(Product=Product,cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(Product=Product,cart=cart) 
            ex_var_list = []
            id = []

            for item in cart_item:
                existing_variation = item.variations.all() 
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if  product_variation in ex_var_list:
                # increase cart_item quantity 
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(Product=Product,id=item_id) 
                item.quantity += 1 
                item.save()

            else:
                item = CartItem.objects.create(Product=Product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()  
        else:
            cart_item = CartItem.objects.create(
                Product = Product,
                quantity = 1,
                cart = cart,
            ) 
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)  
            cart_item.save()  
        return redirect('cart')

def remove_cart(request,product_id,cart_item_id):
   
    Product = get_object_or_404(product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(Product=Product,user = request.user,id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(Product=Product,cart=cart,id=cart_item_id)
        if cart_item.quantity > 1 :
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass        
    return redirect('cart')        

def remove_cart_item(request,product_id,cart_item_id):
    
    Product = get_object_or_404(product,id=product_id)  
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(Product=Product,user = request.user, id=cart_item_id) 
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(Product=Product, cart=cart, id=cart_item_id) 
    cart_item.delete()
    return redirect('cart')  
    
def cart(request,total =0, quantity=0,discount = 0,cart_items=None):
    try:
        disc_price =0
        grand_total=0
        tax=0
        totale=0
        price=0
        if request.user.is_authenticated:
           cart_items = CartItem.objects.filter(user=request.user,is_active=True).order_by('-id') 
        else:   
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            if cart_item.Product.discount:
                print("fdgrdg")
                disc_price =  cart_item.Product.discount * cart_item.quantity
                total += cart_item.Product.discount * cart_item.quantity
                quantity += cart_item.quantity
             
            else:  

                price = cart_item.Product.price * cart_item.quantity      
                quantity += cart_item.quantity  
                total  += cart_item.Product.price * cart_item.quantity  
            tax = (2 * total)/100
            grand_total = total + tax
    except ObjectDoesNotExist:
        pass  

    context ={
        'total' : total,
        'quantity': quantity,
        'cart_items' : cart_items,
        'tax' :tax,
        'discount' : discount,
        'grand_total': grand_total,
        'disc_price' : disc_price,
        'price' :price
        
        
    }     
    return render(request,'accounts/cart.html',context)

def search(request):
    products=0
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            items = product.objects.order_by('-created_at').filter(Q(description__icontains=keyword) | Q(name__icontains=keyword))
            item_count = items.count()
    context = {
        'items':items,
        'item_count':item_count,
    }
    return render(request,'accounts/shop.html',context)


@login_required(login_url='login')
def checkout(request,total=0, quantity=0,cart_item=None):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            data = Address()
            data.user = request.user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form .cleaned_data['city']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.pincode = form.cleaned_data['pincode']

            data.save()
            return redirect('checkout')

    
    try:
        tax=0
        grand_total=0
       

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
            address = Address.objects.filter(user=request.user)
        else:
            # cart = Cart.objects.get(cart_id=_cart_id(request))   
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)

        for cart_item in cart_items:
            if cart_item.Product.discount:
                d = cart_item.Product.price-cart_item.Product.discount
                total += d * cart_item.quantity
                quantity += cart_item.quantity
                tax = (2 * total)/100
                grand_total = total + tax 
            else:
                total += (cart_item.Product.price * cart_item.quantity)
                quantity += cart_item.quantity
            tax = (2 * total)/100
            grand_total = total + tax 
    except ObjectDoesNotExist:
        pass   
    context ={
        'total' : total,
        'quantity': quantity,
        'cart_items' : cart_items,
        'tax' :tax,
        'grand_total': grand_total,
        'address' : address,

    }      
    return render(request,'accounts/checkout.html',context) 

      

def place_order(request,total=0,quantity=0,discount=0):
    current_address = None
    disc_price=0
    cart_item = 0
    tax=0
    grand_total = 0
    data=0
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
   
    if cart_items:
        for cart_item in cart_items:
            if cart_item.Product.discount:
                disc_price =  cart_item.Product.discount * cart_item.quantity
                total += cart_item.Product.discount * cart_item.quantity
                quantity += cart_item.quantity

            else:
                total += (cart_item.Product.price * cart_item.quantity)
                quantity += cart_item.quantity    
        tax = (2 * total)/100
        grand_total = total + tax 
        if 'address' in request.POST:      
            if request.method == 'POST':            
           
                address = request.POST['address']
                current_address = Address.objects.get(id=address)

                data = Order()
                data.user = current_user
                data.address = current_address
                data.order_total = grand_total
                data.tax = tax
                data.discount = discount
                data.ip = request.META.get('REMOTE_ADOR')
                data.save() 

            # generate order_number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")

            order_number = current_date + str(data.id)
            print(order_number)
            data.order_number = order_number
            request.session['order_number'] = order_number
            data.save()
            request.session['order_number']
            
            context = {
                'add' : current_address,  
                'cart_items'  :cart_items,
                'tax' : tax,
                'disount': discount,
                'grand_total' : grand_total,
                'total' : total,
                'disc_price':disc_price
            }

            return render(request,'accounts/payment.html',context)

        else:

            messages.error(request,'Address is required')     
            return redirect('checkout')  

    else:
        return redirect('shop')

def payment(request):
    grand_total = 0
    current_user = request.user     
    cart_items = CartItem.objects.filter(user=current_user) 
    if cart_items :
        total=0
        quantity = 0
        tax = 0
        grand_total = 0
        display =0
        for item in cart_items:
            if item.Product.discount:
                disc_price =  item.Product.discount * item.quantity
                total += item.Product.discount * item.quantity
                quantity += item.quantity
            else:
                total += (item.Product.price * item.quantity)
                quantity += item.quantity    
            tax = (2 * total)/100
            grand_total = total + tax         
        tax = (2 * total)/100
        grand_total = int(total + tax) * 100
        display =  int(total + tax) 
    client = razorpay.Client(auth=(settings.RAZORPAY_ID,settings.RAZORPAY_KEY))

    # create order
    response_payment = client.order.create(dict(amount=grand_total, currency = 'INR'))
    print(response_payment)
    order_id = response_payment['id']
    order_status = response_payment['status']

    if order_status == 'created':

        paym = Payment()
        paym.user = current_user
        print(paym.user)
        paym.amount_paid = grand_total 
        paym.order_id = order_id
        paym.save()
        user = Payment.objects.get(user=current_user,order_id= order_id)
    

    context = {  
        'user' : user,
        'paym' : response_payment,
        'cart_items' :cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
        'total' : total,
        'display' :display
    }
    return render(request,'accounts/razor.html',context)

def payment_status(request):
    response = request.POST
    params_dict = {
        'razorpay_order_id' : response['razorpay_order_id'],
        'razorpay_payment_id' :  response['razorpay_payment_id'],
        'razorpay_signature' :  response['razorpay_signature'],
    }
    #create client instance
    client = razorpay.Client(auth=(settings.RAZORPAY_ID,settings.RAZORPAY_KEY))

    try:
        status = client.utility.verify_payment_signature(params_dict)
        payment = Payment.objects.get(order_id = response['razorpay_order_id'])
        payment.payment_id = response['razorpay_payment_id']
        payment.paid = True
        payment.save()

        order_number = request.session['order_number']
        print(order_number)
        order = Order.objects.get(user=request.user,is_ordered=False,order_number=order_number)
      
        order.is_ordered = True  
        order.status = 'Confirmed'
        order.save()
        cart_items = CartItem.objects.filter(user = request.user)

        for x in cart_items:

            pro_data = OrderProduct()
            pro_data.order_id = order.id
            pro_data.user_id = request.user.id
            pro_data.Product_id = x.Product_id
            pro_data.quantity = x.quantity
            pro_data.payment = payment
            # pro_data.variation = x.variation
            pro_data.product_price= x.Product.price
            pro_data.ordered = True
            pro_data.save()
            
            pr = x.Product
            Product = product.objects.get(id=pr.id)
            Product.stock -= x.quantity
            Product.save()

        cart_items.delete()

        mail_subject = 'THANKYOU FOR SHOPPING WITH US'
        message = render_to_string('accounts/success.html',{
            'user' : request.user,

        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject,message, to =[to_email])  
        send_email.send()

        return render(request,'accounts/payment_status.html',{'status':True})

    except:
        print("gfhfd")
        payment = Payment.objects.get(order_id = response['razorpay_order_id'])
        payment.payment_id = response['razorpay_payment_id']
        payment.paid = True
        payment.save()

        order_number = request.session['order_number']
        print(order_number)
        order = Order.objects.get(user=request.user,order_number=order_number)
        order.is_ordered = False  
        order.status = 'Failed'
        order.save()
        cart_items = CartItem.objects.filter(user = request.user)

        for x in cart_items:

            pro_data = OrderProduct()
            pro_data.order_id = order.id
            pro_data.user_id = request.user.id
            pro_data.Product_id = x.Product_id
            pro_data.quantity = x.quantity
            pro_data.payment = payment
            pro_data.product_price= x.Product.price
            pro_data.ordered = True
            
            pro_data.save()

        return render(request,'accounts/payment_status.html',{'status':False})

@login_required(login_url='login')
def wish_add(request, id):
    Product = product.objects.get(id=id)
    check = WishList.objects.filter(Product=Product).exists()

    if not check:
        wishlist = WishList()
        wishlist.user = request.user
        wishlist.Product = Product
        wishlist.save()

    return redirect('wish_list')

@login_required(login_url='login')
def wish_list(request):
    wish_list= WishList.objects.filter(user=request.user)
    context = { 

        'wish_list' : wish_list, 
    }
    return render(request,'accounts/wishlist.html',context)    

def remove_wish_list(request,product_id):
    Product = WishList.objects.get(Product_id=product_id)
    Product.delete()
   
   
    return redirect('wish_list')  

@login_required(login_url='login')
def profile(request):
    user = Account.objects.get(id=request.user.id)   
    address = Address.objects.filter(user=user)[1:2]

    context = {

        'user' : user,
        'address' : address,
    }
    return render(request,'accounts/profile.html',context)

@login_required(login_url='login')
def edit_profile(request,id):
    try:
        account = Account.objects.get(id=id)
        print(account)
        form = EditProfileUser(instance=account)
        
        if request.method == 'POST':
            form = EditProfileUser(request.POST,instance=account)
            if form.is_valid():
                form.save()
                return redirect('profile')
    except:
        pass 
    context = {

        'form' : form,
    }    
            
    return render(request,'accounts/profile_edit.html',context)         

def delete_address(request,id):
    user = request.user
    current_address = Address.objects.get(user=user,id=id)
    current_address.delete()
    return redirect('checkout')
    
@login_required(login_url='login')
def order_history(request):
    order_product = OrderProduct.objects.filter(user=request.user).order_by('-id')
    order = Order.objects.filter(user=request.user)

    context = {
        'order_product' : order_product,
        'order' : order,
    }

    return render(request,'accounts/order_history.html',context)

def review(request,id):
    ob = OrderProduct.objects.get(id=id)
    Product_id = ob.Product_id
    Product = product.objects.get(id=Product_id)
    form = ReviewForm(initial={'user' : request.user, 'Product':Product})

    if request.method == 'POST':
       images = request.FILES['image']
       review = request.POST['review']
       if 'star' in request.POST:
           rating = request.POST['star']
       else:
           rating = None   

       data = Review()
       data.user = request.user
       data.Product = Product
       data.image = images
       data.review = review
       data.rating = rating
       data.save()
       messages.success(request,'Review updated successfully')
       return redirect('order_history')

    context = {

        'Product' : Product,
        'form' :form,   
    }
    return render(request,'accounts/review.html',context)

def cod(request):
    current_user = request.user  
    tax=0   
    grand_total = 0
    total=0
    cart_items = CartItem.objects.filter(user=current_user) 
    if cart_items :
        total=0
        quantity = 0
        tax = 0
        grand_total = 0
        for item in cart_items:
            if item.Product.discount:
                disc_price =  item.Product.discount * item.quantity
                total += item.Product.discount * item.quantity
                quantity += item.quantity
            else:
                total += (item.Product.price * item.quantity)
                quantity += item.quantity    
            tax = (2 * total)/100
            grand_total = total + tax         
        tax = (2 * total)/100
        grand_total = Decimal(total + tax) 

    if request.method == 'POST':
        grand_total = 0
        total = 0
        tax=0
        recaptcha_response = request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req =  urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())        

        if result['success']:
            messages.success(request, 'Your order placed Successfully!')
            order_number = request.session['order_number']
            print(order_number)
            order = Order.objects.get(user=request.user,order_number=order_number)
            order.is_ordered = True
            order.status = 'Confirmed'
            order.save()
            cart_items = CartItem.objects.filter(user=request.user)

            for x in cart_items:
            
                data = OrderProduct()
                data.order_id = order.id
                data.user_id = request.user.id
                data.Product_id = x.Product_id
                data.quantity = x.quantity
                data.product_price = x.Product.price
                data.ordered = True
                data.save()
                
                prod = x.Product
                Product = product.objects.get(id=prod.id)
                Product.stock -= x.quantity
                Product.save()

            cart_items.delete()    
            mail_subject = 'THANKYOU FOR SHOPPING WITH US'
            message = render_to_string('accounts/success.html',{
                'user' : request.user,
            })
            to_email = request.user.email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

        else:
            messages.error(request,'Invalid reCAPTCHA,Please try again!')        

    context = {
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
        'total' : total,

    }  
    return render(request,'accounts/cod.html',context)  
                






  