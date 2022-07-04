from django import forms
from store.models import Order
from store.models import Section
from store.models import product
from store.models import Variation
from store.models import Brand,Review
from store.models import Category,SubCategory

class CategoryEditForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title','slug']

class SubCategoryEditForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category','name','slug']

class productCreateForm(forms.ModelForm):
    class Meta: 
        model = product
        fields = ['category','subCategory','name','slug','image','description','price','section','brand','is_available','discount','stock']    

    def __init__(self, *args, **kwargs):
        super(productCreateForm,self).__init__(*args, **kwargs)
        self.fields['subCategory'].queryset = SubCategory.objects.none()

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subCategory'].queryset = SubCategory.objects.filter(category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                pass 
        elif self.instance.pk:
            self.fields['subCategory'].queryset = self.instance.category.subcategory_set.order_by('name')     

class VariationForm(forms.ModelForm):
    class Meta:
        model = Variation 
        fields = '__all__'
        
class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = '__all__' 

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status'] 
         
class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['brand_name']


          
