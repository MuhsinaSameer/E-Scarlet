from unicodedata import category
from django.contrib import messages,auth
from django.shortcuts import redirect, render
from requests import request
from accounts.models import Account
from accounts.views import sub_categories
from accounts.views import review
from store.models import Category,SubCategory,Review,Brand,Variation,Order,Section,product,OrderProduct
from .forms import CategoryEditForm, SubCategoryEditForm, VariationForm,  productCreateForm,SectionForm,OrderForm,BrandForm
from django.db.models import Q
from django.db.models import Sum
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
# Create your views here.
acc = Account.objects.filter(is_superadmin = True)

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def admin_table(request):
    costomer_count = Account.objects.filter(is_superadmin=False).count()
    order_count = OrderProduct.objects.filter(ordered=True).count()
    ordered_product = OrderProduct.objects.filter(ordered=True)
    amount = OrderProduct.objects.all()
    total_amount=0
    for x in ordered_product:
        total_amount += x.product_price  
    product_count = product.objects.all().count()

    context = {
        'costomer_count' : costomer_count,
        'order_count' : order_count,
        'ordered_product' : ordered_product,
        'amount' : amount,
        'total_amount' : total_amount,
        'product_count' : product_count
    }  

   
    return render(request,'admins/admin_table.html',context)
    
def product_chart(request):
    labels = []
    data = []  
    queryset = OrderProduct.objects.values('Product__name').annotate(count=Sum('quantity')).order_by('-id')
    for entry in queryset:
        labels.append(entry['Product__name'])
        data.append(entry['count'])

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })    
            
def brand_chart(request):
    labels = []
    data = []  

    queryset = OrderProduct.objects.values('Product__brand').annotate(count=Sum('quantity')).order_by('-id')
    for entry in queryset:
        labels.append(entry['Product__brand'])
        data.append(entry['count'])

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })  
           
@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def manage_user(request):
    user = Account.objects.filter(is_superadmin = False).order_by('-id')
    context = {
        'user' : user,
    }  
    return render(request,'admins/manage_user.html',context)

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')   
def block_user(request,id):
    account = Account.objects.get(id=id)

    if account.is_active:
        account.is_active = False
        account.save()    
    else :
        account.is_active = True
        account.save()
    return redirect('manage_user')     

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def manage_category(request):
    if 'q' in request.GET:
        q = request.GET['q']
        if q:
            category = Category.objects.order_by('title').filter(Q(title__icontains=q)) 
        if not category.exists():
            messages.error(request,'No Matching Datas Found')
            return render(request,'admins/manage_category.html')
    else:
        category = Category.objects.all().order_by('title')    
    context = {
        'category' :category,
    }

    return render(request,'admins/manage_category.html',context)

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def delete_category(request,id):
    category = Category.objects.get(id=id)
    category.delete()
    return redirect('manage_category')

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def edit_category(request,slug):
    category = Category.objects.get(slug=slug)
    form = CategoryEditForm(instance=category)
    try:
        if request.method == 'POST':
            form = CategoryEditForm(request.POST,instance=category)
            if form.is_valid():
                form.save()
                return redirect('manage_category')      
    except:
        messages.error(request,"Slug already exists")
        return redirect('edit_category')  

    context = {
        'form' : form
    }          
    return render(request,'admins/edit_category.html',context)        
        
@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def add_category(request):
    form = CategoryEditForm
    try:
        if request.method == 'POST':
            form = CategoryEditForm(request.POST)
            if form.is_valid():
                form.save()
                print('dfghjk')
                return redirect('manage_category')
        return render (request,'admins/add_category.html',{'form' : form})  
    except:
        messages.error(request,"Slug already exists.")  
        return redirect(request,'add_category')

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def manage_subcategory(request):
    if 'q' in request.GET:
        q = request.GET['q']
        if q:
            subcategory = SubCategory.objects.order_by('name').filter(Q(category__title__icontains=q) | Q(name__icontains=q))
            if not subcategory.exists():
                messages.error(request,'No Matching Datas Found')
                return render(request,'admins/manage_subcategory.html')
    else:
        subcategory = SubCategory.objects.all().order_by('name')       

    context = {
        'subcategory' : subcategory
    }

    return render(request,'admins/manage_subcategory.html',context)    

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def delete_subcategory(request,id):
    subcategory = SubCategory.objects.get(id=id)
    subcategory.delete()
    return redirect('manage_subcategory')

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def edit_subcategory(request,slug):
    subcategory = SubCategory.objects.get(slug=slug)
    form = SubCategoryEditForm(instance=subcategory)   
    try:
        if request.method == 'POST':
            form = SubCategoryEditForm(request.POST,instance=subcategory)
            if form.is_valid():
                form.save()
                return redirect('manage_subcategory')
    except:
        messages.error(request,"Slug already exists.")
        return redirect('edit_subcategory')

    context = {
        'form' : form
    }  
    return render(request,'admins/edit_subcategory.html',context)  

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def add_subcategory(request):
    form = SubCategoryEditForm
    try:
        if request.method == 'POST':
            form = SubCategoryEditForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('manage_subcategory')
        return render (request,'admins/add_subcategory.html',{'form' : form})  
    except:
        messages.error(request,"Slug already exists.")  
        return redirect(request,'add_subcategory')  

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def manage_product(request):

    if 'q' in request.GET:
        q = request.GET['q']
        if q:
            Product = product.objects.order_by('-id').filter(Q(category__title__icontains=q) | Q(subCategory__name__icontains=q)| Q(brand__brand_name__icontains=q))  
            if not Product.exists():
                messages.error(request,'No Matching Datas Found')
                return render(request,'admins/manage_product.html') 
    else:
        Product = product.objects.all().order_by('name')      
                
    context = {
        'Product' : Product
    }  
    return render(request,'admins/manage_product.html',context) 

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def add_product(request):
    form = productCreateForm
    try:
        if request.method == 'POST':
            form = productCreateForm(request.POST, request.FILES) 
            if form.is_valid():
                print('yes')
                form.save()   
                return redirect('manage_product')
            else:
                print("kok")
        return render(request,'admins/add_product.html',{'form':form})  
    except:
        messages.error(request,"Slug already exists.")   
        return redirect('add_subcategory')    

def load_subcategory(request):
    category_id = request.GET.get('category')
    subcategory = SubCategory.objects.filter(category_id=category_id).order_by('name')
    return render(request,'admins/dropdown.html', {'subcategory': subcategory})   

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def delete_product(request,id):
    Product = product.objects.get(id=id)
    Product.delete()
    return redirect('manage_product')

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def edit_product(request,slug):
    Product = product.objects.get(slug=slug)
    form = productCreateForm(instance=Product)
    try:
        if request.method == 'POST':
            form = productCreateForm(request.POST,request.FILES,instance=Product)
            if form.is_valid():
                form.save()  
                return redirect('manage_product') 
    except:
        messages.error(request,"Slug already exists.")  
        return redirect('edit_product')

    context = {
        'form':form
    }
    return render(request,'admins/edit_product.html',context) 

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def manage_variation(request):
    variation=None
    if 'q' in request.GET:
        q = request.GET['q']
        if q:
            variation = Variation.objects.order_by('-id').filter(Q(Product__name__icontains=q)  | Q(variation_category__icontains=q) | Q(variation_value__icontains=q))
            if not variation.exists():
                return render(request,'admins/manage_variation.html')
        else:
            return redirect('manage_variation')        
    else:
        variation = Variation.objects.all().order_by('-Product') 
    context = {

        'variation' : variation,
    }  
    return render(request,'admins/manage_variation.html',context)

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def delete_variation(request,id):
    variation = Variation.objects.get(id=id)
    variation.delete()
    return redirect('manage_variation')

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def add_variation(request):
    form = VariationForm
    if request.method == 'POST':
        form = VariationForm(request.POST) 
        if form.is_valid():
            form.save() 
            return redirect('manage_variation')

    return render(request,'admins/add_variation.html',{'form':form})  

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def edit_vatiation(request,id):
    variation = Variation.objects.get(id=id)
    form = VariationForm(instance=variation)

    if request.method == 'POST':
        form = VariationForm(request.POST,instance=variation)
        if form.is_valid():
            form.save()
            return redirect('manage_variation')
    context = {
        'form' : form
    }
    return render(request,'admins/add_variation.html')  

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def manage_section(request):
    if 'q' in request.GET:
        q = request.GET['q']
        if q:
            section = Section.objects.order_by('-id').filter(Q(name__icontains=q))
            if not section.exists():
                messages.error(request,'No Matching Datas Found')
                return render(request,'admins/manage_section.html') 
    else:
        section = Section.objects.all().order_by('name')     

    context = {
        'section' : section
    }
    return render(request,'admins/manage_section.html',context)

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def delete_section(request,id):
    section = Section.objects.get(id=id)
    section.delete()
    return redirect('manage_section')

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def edit_section(request,id):
    section = Section.objects.get(id=id)
    form = SectionForm(instance=section)
    try:
        if request.method == 'POST':
            form = SectionForm(request.POST,instance=section)
            form.is_valid()
            form.save()
            return redirect('manage_section')
    except:
        
        return redirect('edit_section') 

    context = {
        'form' : form
    }       
    return render(request,'admins/add_section.html',context)

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def add_section(request):
    form = SectionForm
    try:
        if request.method == 'POST':
           form = SectionForm(request.POST)
           if form.is_valid():
               form.save()
               return redirect('manage_section')
        return render(request,'admins/add_section.html',{'form' : form})  
    except: 
        return redirect(request,'add_section') 

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def manage_brand(request):
    if 'q' in request.GET:
        q = request.GET['q']
        if q :
            brand = Brand.objects.order_by('-id').filter(Q(brand_name__icontains=q))  
            if not brand.exists():
                return render(request,'admins/manage_brand.html')
        else:
            return redirect('manage_brand')  
    else:
        brand = Brand.objects.all().order_by('-id')  

    context = {

        'brand' : brand,
    }
    return render(request,'admins/manage_brand.html',context)  

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def edit_brand(request,id):
    brand = Brand.objects.get(id=id)
    form = BrandForm(instance=brand)
    try:
        if request.method == 'POST':
            form = SectionForm(request.POST,instance=brand)
            form.is_valid()
            form.save()
            return redirect('manage_brand')
    except:
        
        return redirect('edit_brand') 

    context = {
        'form' : form
    }       
    return render(request,'admins/add_brand.html',context) 

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def delete_brand(request,id):
    brand = Brand.objects.get(id=id)
    brand.delete()
    return redirect('manage_brand')

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def add_brand(request):
    form = BrandForm
    try:
        if request.method == 'POST':
           form = BrandForm(request.POST)
           if form.is_valid():
               form.save()
               return redirect('manage_brand')
        return render(request,'admins/add_brand.html',{'form' : form})  
    except: 
        return redirect(request,'add_brand') 
    
                         
@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def manage_order(request):
    if 'q' in request.GET:
        q = request.GET['q']
        if q :
            order = Order.objects.order_by('-id').filter(Q(order_number__icontains=q))
            order_product =OrderProduct.objects.all()
            if not order.exists():
                return render(request,'admins/manage_order.html')
        else:
            return redirect('manage_order')
    else:
        order = Order.objects.all().order_by('-id')     
        order_product = OrderProduct.objects.all()       

    context = {
        'order' : order,
        'order_product' : order_product,
    }
    return render(request,'admins/manage_order.html',context)

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def edit_order(request,id):
    order = Order.objects.get(id=id)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST,instance=order)
        if form.is_valid():
            form.save()
            return redirect('manage_order')
    context = {
        'form' : form,
    } 
    return render(request,'admins/edit_order.html',context)       

def admin_logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out')
    return redirect('login')

def admin_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            if user.is_superadmin:
                auth.login(request,user)
                return redirect('admin_table')
              
        else:
            messages.error(request,'Invalid login credentials!!')  
            return redirect('admin_login')

    return render(request,'admins/admin_login.html')

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def manage_review(request):
    if 'q' in request.GET:
        q = request.GET['q']
        if q :
            review = Review.objects.order_by('-id').filter(Q(user__first_name__icontains=q))
            if not review.exists():
                return render(request,'admins/manage_review.html')
        else:
            return redirect('manage_review')
    else:
        review = Review.objects.all().order_by('-id')     
        

    context = {
        'review' : review,
    }
    return render(request,'admins/manage_review.html',context)

@user_passes_test(lambda u: u in acc, login_url = 'admin_login')
def delete_review(request,id):
    review = Review.objects.get(id=id)
    review.delete()
    return redirect('manage_review')    
