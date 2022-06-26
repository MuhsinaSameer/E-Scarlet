from django.contrib import admin
from .models import Address, Category, Order, Payment,SubCategory, Brand, Variation, WishList, product, Section,Cart,CartItem,Variation,Order,OrderProduct,Payment
from .models import WishList,Review
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('title',)}
    list_display = ('title','slug')

class SubCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
    list_display = ('name','slug')

class productAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
    list_display = ('name','slug')

class VariationAdmin(admin.ModelAdmin):
    list_display = ('Product', 'variation_category','variation_value','is_active')
    list_editable = ('is_active',)
    list_filter =  ('Product', 'variation_category','variation_value')

class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id','date_added')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('Product','cart','quantity','is_active')    
    


admin.site.register(Category,CategoryAdmin)
admin.site.register(SubCategory,SubCategoryAdmin)
admin.site.register(product,productAdmin)
admin.site.register(Section)
admin.site.register(Brand)
admin.site.register(Cart,CartAdmin)
admin.site.register(CartItem,CartItemAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(Payment)
admin.site.register(WishList)
admin.site.register(Review)