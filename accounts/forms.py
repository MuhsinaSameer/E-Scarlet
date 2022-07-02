
from django import forms

from store.models import Review
from .models import Account
from store.models import Address 
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'',
        'class':'form_control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':''
    }))    
    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password']

    def __init__(self,*args,**kwargs): 
        super(RegistrationForm,self).__init__(*args,**kwargs) 
        self.fields['first_name'].widget.attrs['placeholder'] = ''
        self.fields['last_name'].widget.attrs['placeholder'] = ''  
        self.fields['phone_number'].widget.attrs['placeholder'] = '' 
        self.fields['email'].widget.attrs['placeholder'] = '' 
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form_control'

    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()
        password = cleaned_data.get('password') 
        confirm_password = cleaned_data.get('confirm_password')
        

        if password != confirm_password:
            raise forms.ValidationError(
                "Password doesn't match!"
            )

        if len(password)<8:
            raise forms.ValidationError(
                "Password must contain minimum 8 characters"
            )
            
class VerifyForm(forms.Form):
    code = forms.CharField(max_length=8, required=True, help_text='')            

           
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['first_name','last_name','phone','email','address_line_1','address_line_2','country','state','city','pincode']

class EditProfileUser(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name','last_name','username']     

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['image','review']         
