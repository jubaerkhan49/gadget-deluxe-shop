from django import forms
from store.models import Product, ProductImage, FAQ, StoreSettings, IPhoneModel
from orders.models import Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'model',
            'title',
            'title_bn',
            'storage',
            'color',
            'color_bn',
            'condition',
            'battery_health',
            'sim_type',
            'origin_region',
            'masked_imei',
            'price',
            'original_price',
            'primary_image',
            'description',
            'description_bn',
            'warranty_info',
            'status',
            'featured',
        ]
        widgets = {
            'model': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none'}),
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none', 'placeholder': 'e.g. iPhone 15 Pro Max 256GB Natural Titanium (99% Like New)'}),
            'title_bn': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none', 'placeholder': 'বাংলা শিরোনাম'}),
            'storage': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none'}),
            'color': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none', 'placeholder': 'e.g. Natural Titanium, Space Black'}),
            'color_bn': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none', 'placeholder': 'e.g. ন্যাচারাল টাইটানিয়াম'}),
            'condition': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none'}),
            'battery_health': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none', 'min': 50, 'max': 100}),
            'sim_type': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none'}),
            'origin_region': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none', 'placeholder': 'e.g. USA (LL/A), Japan (J/A)'}),
            'masked_imei': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none', 'placeholder': 'e.g. 3549********812'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none', 'placeholder': 'e.g. 109000'}),
            'original_price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none', 'placeholder': 'e.g. 115000 (Optional)'}),
            'primary_image': forms.FileInput(attrs={'class': 'w-full px-3 py-2 rounded-xl border border-zinc-200 bg-zinc-50 text-xs'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none', 'rows': 3, 'placeholder': 'Inspection test score, 3uTools results, body condition details...'}),
            'description_bn': forms.Textarea(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none', 'rows': 3, 'placeholder': 'বাংলা বিবরণ...'}),
            'warranty_info': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none'}),
            'featured': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-black rounded border-zinc-300 focus:ring-black'}),
        }


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'order']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'w-full text-xs'}),
            'alt_text': forms.TextInput(attrs={'class': 'w-full px-3 py-1.5 rounded-lg border border-zinc-200 text-xs', 'placeholder': 'Alt text / Photo description'}),
            'order': forms.NumberInput(attrs={'class': 'w-20 px-3 py-1.5 rounded-lg border border-zinc-200 text-xs'}),
        }


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['category', 'question_en', 'question_bn', 'answer_en', 'answer_bn', 'order', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none'}),
            'question_en': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none', 'placeholder': 'Question in English'}),
            'question_bn': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none', 'placeholder': 'প্রশ্ন (বাংলায়)'}),
            'answer_en': forms.Textarea(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none', 'rows': 4, 'placeholder': 'Detailed Answer in English'}),
            'answer_bn': forms.Textarea(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none', 'rows': 4, 'placeholder': 'বিস্তারিত উত্তর (বাংলায়)'}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-zinc-200 bg-white text-sm focus:ring-2 focus:ring-black focus:outline-none'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-black rounded border-zinc-300 focus:ring-black'}),
        }


class StoreSettingsForm(forms.ModelForm):
    class Meta:
        model = StoreSettings
        fields = [
            'store_name',
            'tagline_en',
            'tagline_bn',
            'phone_number',
            'whatsapp_number',
            'email',
            'address_en',
            'address_bn',
            'delivery_charge_inside_dhaka',
            'delivery_charge_outside_dhaka',
            'warranty_badge_en',
            'warranty_badge_bn',
            'bkash_number',
            'bkash_instructions_en',
            'bkash_instructions_bn',
            'nagad_number',
            'nagad_instructions_en',
            'nagad_instructions_bn',
            'rocket_number',
            'rocket_instructions_en',
            'rocket_instructions_bn',
            'bank_details_en',
            'bank_details_bn',
        ]
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'tagline_en': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'tagline_bn': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'address_en': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'address_bn': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'delivery_charge_inside_dhaka': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'delivery_charge_outside_dhaka': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'warranty_badge_en': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'warranty_badge_bn': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'bkash_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'bkash_instructions_en': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'bkash_instructions_bn': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'nagad_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'nagad_instructions_en': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'nagad_instructions_bn': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'rocket_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'rocket_instructions_en': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'rocket_instructions_bn': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black'}),
            'bank_details_en': forms.Textarea(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black', 'rows': 4}),
            'bank_details_bn': forms.Textarea(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-zinc-200 text-sm focus:ring-2 focus:ring-black', 'rows': 4}),
        }


class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_status', 'payment_status']
        widgets = {
            'order_status': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-xl border border-zinc-200 bg-white text-xs font-semibold focus:ring-2 focus:ring-black focus:outline-none'}),
            'payment_status': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-xl border border-zinc-200 bg-white text-xs font-semibold focus:ring-2 focus:ring-black focus:outline-none'}),
        }
