from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
import re


class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none transition',
            'placeholder': 'Your Full Name / আপনার পুরো নাম',
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none transition',
            'placeholder': 'name@example.com',
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none transition',
            'placeholder': '01XXXXXXXXX',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'phone']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none transition',
                'placeholder': 'Choose a username / ইউজারনেম',
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['password1', 'password2']:
            if fieldname in self.fields:
                self.fields[fieldname].widget.attrs.update({
                    'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none transition',
                })

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip().replace(' ', '').replace('-', '')
        if phone.startswith('+88'):
            phone = phone[3:]
        elif phone.startswith('88'):
            phone = phone[2:]
        if not re.match(r'^01[3-9]\d{8}$', phone):
            raise forms.ValidationError("Please enter a valid 11-digit Bangladeshi mobile number.")
        return phone


class CustomerLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none transition',
            'placeholder': 'Username or Email',
            'autocomplete': 'off',
            'readonly': 'readonly',
            'onfocus': "this.removeAttribute('readonly');",
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none transition',
            'placeholder': '••••••••',
            'autocomplete': 'new-password',
            'readonly': 'readonly',
            'onfocus': "this.removeAttribute('readonly');",
        })
