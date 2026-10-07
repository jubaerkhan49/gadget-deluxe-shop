from django import forms
from .models import Order
import re


class CheckoutForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=[
            ('cod', 'Cash on Delivery (COD)'),
            ('bank_transfer', 'Bank Transfer'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'payment-method-radio focus:ring-black'}),
        initial='cod',
    )

    class Meta:
        model = Order
        fields = [
            'full_name',
            'phone',
            'email',
            'delivery_address',
            'city',
            'delivery_notes',
            'payment_method',
            'payment_sender_number',
            'payment_trx_id',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none transition',
                'placeholder': 'e.g. Tanvir Ahmed',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none transition',
                'placeholder': '01XXXXXXXXX',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none transition',
                'placeholder': 'name@example.com (Optional)',
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none transition',
                'rows': 3,
                'placeholder': 'House #, Road #, Sector/Area, Landmark',
                'required': True,
            }),
            'city': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none transition',
                'id': 'id_city',
            }),
            'delivery_notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none transition',
                'rows': 2,
                'placeholder': 'e.g. Call before delivery, deliver after 3 PM (Optional)',
            }),
            'payment_sender_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none transition',
                'placeholder': 'Sender Phone or Bank Account Name',
            }),
            'payment_trx_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none transition',
                'placeholder': 'e.g. Bank Deposit Ref / Slip No',
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip().replace(' ', '').replace('-', '')
        if phone.startswith('+88'):
            phone = phone[3:]
        elif phone.startswith('88'):
            phone = phone[2:]
            
        if not re.match(r'^01[3-9]\d{8}$', phone):
            raise forms.ValidationError("Please enter a valid 11-digit Bangladeshi mobile number (e.g. 017XXXXXXXX).")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('payment_method')
        sender = cleaned_data.get('payment_sender_number')
        trx_id = cleaned_data.get('payment_trx_id')

        # If bKash, Nagad, or Rocket is selected, encourage entering TrxID
        if method in ['bkash', 'nagad', 'rocket']:
            if not trx_id:
                self.add_error('payment_trx_id', 'Please provide the Transaction ID (TrxID) for verification.')
        elif method == 'bank_transfer':
            if not trx_id:
                self.add_error('payment_trx_id', 'Please provide the Bank Deposit / Transfer Reference number.')

        return cleaned_data


class OrderTrackSearchForm(forms.Form):
    order_number = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none uppercase font-mono',
            'placeholder': 'e.g. GD839214',
            'required': True,
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none',
            'placeholder': '01XXXXXXXXX',
            'required': True,
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip().replace(' ', '').replace('-', '')
        if phone.startswith('+88'):
            phone = phone[3:]
        elif phone.startswith('88'):
            phone = phone[2:]
        return phone
