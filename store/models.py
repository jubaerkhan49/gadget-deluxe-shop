from django.db import models
from django.utils.text import slugify
from django.urls import reverse
import uuid


class IPhoneModel(models.Model):
    MODEL_CHOICES = [
        ('iPhone 14 Pro', 'iPhone 14 Pro'),
        ('iPhone 14 Pro Max', 'iPhone 14 Pro Max'),
        ('iPhone 15 Pro', 'iPhone 15 Pro'),
        ('iPhone 15 Pro Max', 'iPhone 15 Pro Max'),
        ('iPhone 16 Pro', 'iPhone 16 Pro'),
        ('iPhone 16 Pro Max', 'iPhone 16 Pro Max'),
    ]

    name = models.CharField(max_length=50, choices=MODEL_CHOICES, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    release_year = models.IntegerField(default=2023)
    order = models.PositiveIntegerField(default=0, help_text="Order in filters/lists")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "iPhone Model"
        verbose_name_plural = "iPhone Models"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    STORAGE_CHOICES = [
        ('128GB', '128GB'),
        ('256GB', '256GB'),
        ('512GB', '512GB'),
        ('1TB', '1TB'),
    ]

    CONDITION_CHOICES = [
        ('like_new', 'Like New / Pristine (99%)'),
        ('excellent', 'Excellent Condition (95%+)'),
        ('good', 'Good Condition (90%+)'),
    ]

    SIM_CHOICES = [
        ('physical_esim', '1 Physical SIM + 1 eSIM'),
        ('dual_esim', 'Dual eSIM (USA Variant)'),
        ('dual_physical', 'Dual Physical SIM (HK/China/Global)'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available for Sale'),
        ('reserved', 'Reserved (In Order)'),
        ('sold', 'Sold Out'),
    ]

    sku = models.CharField(
        max_length=30, 
        unique=True, 
        blank=True, 
        help_text="Unique device listing code e.g. GD-15PM-882"
    )
    title = models.CharField(max_length=200, help_text="e.g. iPhone 15 Pro Max 256GB Natural Titanium (99% Like New)")
    title_bn = models.CharField(max_length=200, blank=True, help_text="বাংলা শিরোনাম")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    model = models.ForeignKey(IPhoneModel, on_delete=models.CASCADE, related_name='products')
    
    storage = models.CharField(max_length=10, choices=STORAGE_CHOICES, default='256GB')
    color = models.CharField(max_length=50, help_text="e.g. Natural Titanium, Deep Purple, Space Black")
    color_bn = models.CharField(max_length=50, blank=True, help_text="e.g. ন্যাচারাল টাইটানিয়াম")
    
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='like_new')
    battery_health = models.PositiveIntegerField(
        help_text="Battery Health Percentage (e.g. 96 for 96%)",
        default=100
    )
    sim_type = models.CharField(max_length=20, choices=SIM_CHOICES, default='physical_esim')
    origin_region = models.CharField(
        max_length=50, 
        default='USA (LL/A)', 
        help_text="e.g. USA (LL/A), Japan (J/A), Singapore (ZA/A)"
    )
    masked_imei = models.CharField(
        max_length=30, 
        blank=True, 
        help_text="e.g. 3549********812 (for customer trust)"
    )

    price = models.DecimalField(max_digits=10, decimal_places=0, help_text="Selling price in BDT (৳)")
    original_price = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        null=True, 
        blank=True, 
        help_text="Optional previous price for discount display (৳)"
    )

    description = models.TextField(
        blank=True,
        help_text="Device history, inspection test report summary (3uTools 100% score, TrueTone, FaceID working)."
    )
    description_bn = models.TextField(blank=True, help_text="বাংলা বিবরণ")

    primary_image = models.ImageField(upload_to='products/', blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')
    featured = models.BooleanField(default=False, help_text="Feature on Homepage")
    warranty_info = models.CharField(
        max_length=150, 
        default="7 Days Replacement & 1 Year Free Service Warranty",
        help_text="Warranty guarantee for this phone"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-featured', '-created_at']
        verbose_name = "Used iPhone Listing"
        verbose_name_plural = "Used iPhone Listings"

    def __str__(self):
        return f"{self.title} ({self.sku or self.id}) - ৳{self.price:,}"

    def save(self, *args, **kwargs):
        if not self.sku:
            clean_model = self.model.name.replace('iPhone ', '').replace(' ', '')
            rand_code = uuid.uuid4().hex[:4].upper()
            self.sku = f"GD-{clean_model}-{rand_code}"
        
        if not self.slug:
            base_slug = slugify(f"{self.model.name}-{self.storage}-{self.color}-{self.sku}")
            self.slug = base_slug
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    @property
    def is_in_stock(self):
        return self.status == 'available'

    @property
    def condition_display_bn(self):
        if self.condition == 'like_new':
            return 'লাইক নিউ (৯৯%)'
        elif self.condition == 'excellent':
            return 'চমৎকার কন্ডিশন (৯৫%+)'
        return 'ভালো কন্ডিশন (৯০%+)'

    @property
    def sim_display_bn(self):
        if self.sim_type == 'physical_esim':
            return '১ ফিজিক্যাল সিম + ১ ই-সিম'
        elif self.sim_type == 'dual_esim':
            return 'ডুয়াল ই-সিম (USA ভ্যারিয়েন্ট)'
        return 'ডুয়াল ফিজিক্যাল সিম (HK/China)'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=150, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Product Image"
        verbose_name_plural = "Product Gallery Images"

    def __str__(self):
        return f"Image for {self.product.sku}"


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('quality', 'Device Quality & Testing / গুণমান ও পরীক্ষণ'),
        ('battery', 'Battery & Warranty / ব্যাটারি ও ওয়ারেন্টি'),
        ('order', 'Ordering & Delivery / অর্ডার ও ডেলিভারি'),
        ('payment', 'Payment Methods / পেমেন্ট মাধ্যম'),
    ]

    question_en = models.CharField(max_length=300, verbose_name="Question (English)")
    question_bn = models.CharField(max_length=300, verbose_name="প্রশ্ন (বাংলা)")
    answer_en = models.TextField(verbose_name="Answer (English)")
    answer_bn = models.TextField(verbose_name="উত্তর (বাংলা)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='quality')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "FAQ Item"
        verbose_name_plural = "FAQ Items"

    def __str__(self):
        return self.question_en


class StoreSettings(models.Model):
    store_name = models.CharField(max_length=100, default="Gadget Deluxe")
    tagline_en = models.CharField(max_length=200, default="Quality Used iPhones, Carefully Checked.")
    tagline_bn = models.CharField(max_length=200, default="যাচাইকৃত সেরা মানের ব্যবহৃত আইফোন।")
    
    phone_number = models.CharField(max_length=30, default="+880 1700-000000")
    whatsapp_number = models.CharField(max_length=30, default="+880 1700-000000")
    email = models.EmailField(default="support@gadgetdeluxe.shop")
    address_en = models.CharField(max_length=255, default="Shop #42, Level 4, Bashundhara City / Multiplan Center, Dhaka")
    address_bn = models.CharField(max_length=255, default="শপ #৪২, লেভেল ৪, বসুন্ধরা সিটি / মাল্টিপ্ল্যান সেন্টার, ঢাকা")

    # Payment accounts
    bkash_number = models.CharField(max_length=50, default="017XXXXXXXX (Personal/Merchant)")
    bkash_instructions_en = models.CharField(
        max_length=255, 
        default="Send Money or Merchant Payment to our bKash number and enter TrxID below."
    )
    bkash_instructions_bn = models.CharField(
        max_length=255, 
        default="আমাদের বিকাশ নম্বরে সেন্ড মানি বা পেমেন্ট করে নিচে ট্রানজেকশন আইডি (TrxID) দিন।"
    )

    nagad_number = models.CharField(max_length=50, default="017XXXXXXXX (Personal/Merchant)")
    nagad_instructions_en = models.CharField(
        max_length=255, 
        default="Send Money to our Nagad number and provide sender number and TrxID."
    )
    nagad_instructions_bn = models.CharField(
        max_length=255, 
        default="আমাদের নগদ নম্বরে সেন্ড মানি করে প্রেরকের নম্বর এবং TrxID দিন।"
    )

    rocket_number = models.CharField(max_length=50, default="017XXXXXXXX-X (Personal)")
    rocket_instructions_en = models.CharField(
        max_length=255, 
        default="Send Money to our Rocket number and provide your TrxID."
    )
    rocket_instructions_bn = models.CharField(
        max_length=255, 
        default="আমাদের রকেট নম্বরে সেন্ড মানি করে TrxID দিন।"
    )

    bank_details_en = models.TextField(
        default="Bank: The City Bank Ltd\nAccount Name: Gadget Deluxe\nAccount Number: 150120XXXXXXXXXX\nBranch: Gulshan, Dhaka\nRouting: 06027XXXX"
    )
    bank_details_bn = models.TextField(
        default="ব্যাংক: দ্য সিটি ব্যাংক লিমিটেড\nহিসাবের নাম: গ্যাজেট ডিলাক্স\nহিসাব নম্বর: 150120XXXXXXXXXX\nশাখা: গুলশান, ঢাকা"
    )

    # Delivery Charges
    delivery_charge_inside_dhaka = models.DecimalField(max_digits=6, decimal_places=0, default=100)
    delivery_charge_outside_dhaka = models.DecimalField(max_digits=6, decimal_places=0, default=150)

    # Warranty badge
    warranty_badge_en = models.CharField(max_length=150, default="7 Days Replacement & 1 Year Free Service Warranty")
    warranty_badge_bn = models.CharField(max_length=150, default="৭ দিনের রিপ্লেসমেন্ট এবং ১ বছরের ফ্রি সার্ভিস ওয়ারেন্টি")

    class Meta:
        verbose_name = "Store & Payment Settings"
        verbose_name_plural = "Store & Payment Settings"

    def __str__(self):
        return f"{self.store_name} Settings"

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj
