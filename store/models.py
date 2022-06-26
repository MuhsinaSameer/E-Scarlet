from unicodedata import name
from django.db import models
from django.forms import DateTimeField
from django.urls import reverse
from requests import request

from accounts.models import Account
# Create your models here.


class Category(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True,max_length=50)

    def get_url(self):
        return reverse('products_by_category',args=[self.slug]) 

    def __str__(self):
        return self.title
    


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def get_url(self):
        return reverse('products_by_subCategory',args=[self.category.slug,self.slug])

    def __str__(self):
        return self.name

class Section(models.Model):    
    name = models.CharField(max_length=50)

    def __str__(self):        
        return self.name

class Brand(models.Model):
    brand_name = models.CharField(max_length=50) 

    def __str__(self):
        return self.brand_name

class product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subCategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE,null=True,blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE,null=True,blank=True)

    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200,unique=True)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    description = models.TextField(max_length=300)
    discount = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True)
    stock = models.IntegerField()
    image = models.ImageField(upload_to = 'images')
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    
    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.subCategory.slug,self.slug])

    def __str__(self):
        return self.name

class Cart(models.Model):
    cart_id = models.CharField(max_length=250,blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category='color',is_active=True)   


variation_category_choice = (
    ('color','color'),
)        

class Variation(models.Model):
    Product = models.ForeignKey(product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100,choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    cerated_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value

class CartItem(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    Product = models.ForeignKey(product,on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation,blank=True)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)


    def sub_total(self):
        return self.Product.price * self.quantity

 
    def subdesc_total(self):
        return self.Product.discount * self.quantity



    def __unicode__(self):
        return self.Product

class WishList(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    Product = models.ForeignKey(product,on_delete=models.CASCADE)  


    def __str__(self):
        return self.user.email

class Address(models.Model):
    TYPE = (
        ('Home','Home'),
        ('Office','Office'),
    )
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pincode = models.CharField(max_length=50)
    type = models.CharField(max_length=50,choices=TYPE,default='Home')

    def __str__(self):
        return self.first_name

class Payment(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    payment_id = models.CharField(max_length=100)
    order_id = models.CharField(max_length=100,blank=True)
    amount_paid = models.CharField(max_length=100)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name

class Order(models.Model):
    STATUS = (
        ('New','New'),
        ('Accepted','Accepted'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
        ('Confirmed','Confirmed'),
        ('Failed','Failed'),
        ('Delivered','Delivered')
    )    
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    payment =  models.ForeignKey(Payment,on_delete=models.CASCADE,null=True,blank=True)  
    order_number = models.CharField(max_length=20) 
    address = models.ForeignKey(Address,on_delete=models.CASCADE)
    order_total = models.FloatField()
    tax = models.FloatField()
    discount =  models.FloatField(blank = True,null = True)
    status = models.CharField(max_length=10,choices=STATUS,default='New')
    ip = models.CharField(blank = True,max_length=20,null=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_number

class OrderProduct(models.Model):
    order =  models.ForeignKey(Order,on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    user =  models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    Product = models.ForeignKey(product,on_delete=models.CASCADE)
    variation =  models.ForeignKey(Variation,blank=True,on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Product.name

class Review(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    Product = models.ForeignKey(product,on_delete=models.CASCADE) 
    image = models.ImageField(upload_to = 'review',null = True,blank = True)
    review = models.TextField(max_length=300)
    rating = models.IntegerField(null = True,blank = True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Product.name
       
    
