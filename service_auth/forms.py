from django import forms
from django.contrib.auth.models import User as AuthUser
#from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _ # per i form va usato questo


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput,
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
    )
    
class RegisterForm(forms.ModelForm):
    username = forms.CharField(help_text='')
    password = forms.CharField(
        widget=forms.PasswordInput,
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label=_('Confirm password'),
    )

    class Meta:
        model = AuthUser
        fields = ['username', 'password']

    def clean(self):
        cleaned_data = super().clean() 
        password  = cleaned_data['password']       
        password_confirm  = cleaned_data['password_confirm']       
        if password != password_confirm:
            raise forms.ValidationError(_('Password don\'t match'))
        return cleaned_data
    
  