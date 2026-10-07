from django import forms
from store.models import Product, ProductImage, FAQ, StoreSettings, IPhoneModel
from orders.models import Order


# Unified styling classes for form inputs that look crisp in both light and dark mode
INPUT_CLASSES = (
    "w-full px-4 py-2.5 rounded-xl border border-zinc-300 dark:border-zinc-700 "
    "bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-sm "
    "placeholder:text-zinc-400 dark:placeholder:text-zinc-500 "
    "focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white transition"
)

SELECT_CLASSES = (
    "w-full px-4 py-2.5 rounded-xl border border-zinc-300 dark:border-zinc-700 "
    "bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-sm "
    "focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white transition"
)

TEXTAREA_CLASSES = (
    "w-full px-4 py-2.5 rounded-xl border border-zinc-300 dark:border-zinc-700 "
    "bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-sm "
    "placeholder:text-zinc-400 dark:placeholder:text-zinc-500 "
    "focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white transition"
)


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
            'cycle_count',
            'sim_type',
            'price',
            'original_price',
            'display_inspection',
            'truetone_inspection',
            'faceid_inspection',
            'sound_inspection',
            'charging_inspection',
            'camera_inspection',
            'flashlight_inspection',
            'primary_image',
            'description',
            'description_bn',
            'status',
            'featured',
        ]
        widgets = {
            'model': forms.Select(attrs={'class': SELECT_CLASSES}),
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g. iPhone 15 Pro Max 256GB Natural Titanium (99% Like New)'}),
            'title_bn': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'বাংলা শিরোনাম'}),
            'storage': forms.Select(attrs={'class': SELECT_CLASSES}),
            'color': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g. Natural Titanium, Space Black'}),
            'color_bn': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g. ন্যাচারাল টাইটানিয়াম'}),
            'condition': forms.Select(attrs={'class': SELECT_CLASSES}),
            'battery_health': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'min': 50, 'max': 100, 'placeholder': 'e.g. 96'}),
            'cycle_count': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'min': 0, 'placeholder': 'e.g. 140'}),
            'sim_type': forms.Select(attrs={'class': SELECT_CLASSES}),
            'price': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g. 109000'}),
            'original_price': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g. 115000 (Optional)'}),
            'display_inspection': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g. 120Hz ProMotion OLED: OK'}),
            'truetone_inspection': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g. TrueTone: OK'}),
            'faceid_inspection': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g. FaceID & Sensors: Working'}),
            'sound_inspection': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g. Sound & Vibration: OK'}),
            'charging_inspection': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g. Charging: OK'}),
            'camera_inspection': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g. Camera: OK'}),
            'flashlight_inspection': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g. Flashlight: OK'}),
            'primary_image': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 rounded-xl border border-zinc-300 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-900 text-xs text-zinc-900 dark:text-zinc-100',
                'accept': 'image/*,.heic,.heif,.HEIC,.HEIF'
            }),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 3, 'placeholder': 'Inspection test results, body condition details...'}),
            'description_bn': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 3, 'placeholder': 'বাংলা বিবরণ...'}),
            'status': forms.Select(attrs={'class': SELECT_CLASSES}),
            'featured': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-black rounded border-zinc-300 dark:border-zinc-700 focus:ring-black'}),
        }

    def clean_primary_image(self):
        img = self.cleaned_data.get('primary_image')
        if img and hasattr(img, 'file'):
            from store.image_utils import process_image_file
            return process_image_file(img)
        return img


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'w-full text-xs text-zinc-900 dark:text-zinc-100',
                'accept': 'image/*,.heic,.heif,.HEIC,.HEIF'
            }),
            'alt_text': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Alt text / Photo description'}),
            'order': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
        }

    def clean_image(self):
        img = self.cleaned_data.get('image')
        if img and hasattr(img, 'file'):
            from store.image_utils import process_image_file
            return process_image_file(img)
        return img


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['category', 'question_en', 'question_bn', 'answer_en', 'answer_bn', 'order', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': SELECT_CLASSES}),
            'question_en': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Question in English'}),
            'question_bn': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'প্রশ্ন (বাংলায়)'}),
            'answer_en': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 4, 'placeholder': 'Detailed Answer in English'}),
            'answer_bn': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 4, 'placeholder': 'বিস্তারিত উত্তর (বাংলায়)'}),
            'order': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-black rounded border-zinc-300 dark:border-zinc-700 focus:ring-black'}),
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
            'store_name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'tagline_en': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'tagline_bn': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'phone_number': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'whatsapp_number': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASSES}),
            'address_en': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'address_bn': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'delivery_charge_inside_dhaka': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'delivery_charge_outside_dhaka': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'warranty_badge_en': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'warranty_badge_bn': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'bkash_number': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'bkash_instructions_en': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'bkash_instructions_bn': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'nagad_number': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'nagad_instructions_en': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'nagad_instructions_bn': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'rocket_number': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'rocket_instructions_en': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'rocket_instructions_bn': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'bank_details_en': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 4}),
            'bank_details_bn': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 4}),
        }


class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_status', 'payment_status']
        widgets = {
            'order_status': forms.Select(attrs={'class': SELECT_CLASSES}),
            'payment_status': forms.Select(attrs={'class': SELECT_CLASSES}),
        }
