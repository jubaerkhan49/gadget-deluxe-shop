from django.db import models
from django.contrib.auth.models import User
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
        ('like_new', '99%+ New'),
        ('excellent', '95%+ New'),
        ('good', '90%+ New'),
    ]

    QUALITY_GRADE_CHOICES = [
        ('Perfect', 'Perfect'),
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor'),
    ]

    OK_NOT_OK_CHOICES = [
        ('OK', 'OK'),
        ('Not OK', 'Not OK'),
    ]

    WORKING_CHOICES = [
        ('Working', 'Working'),
        ('Not Working', 'Not Working'),
    ]

    SIM_CHOICES = [
        ('physical_esim', '1 Physical SIM + 1 eSIM'),
        ('dual_esim', 'Dual eSIM (USA Variant)'),
        ('dual_physical', 'Dual Physical SIM (HK/China/Global)'),
        ('wifi_only', 'WiFi Only'),
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
    cycle_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=0,
        help_text="Battery Cycle Count (e.g. 120)"
    )
    sim_type = models.CharField(max_length=20, choices=SIM_CHOICES, default='physical_esim')
    origin_region = models.CharField(
        max_length=50, 
        blank=True, 
        default='', 
        help_text="Optional origin e.g. USA (LL/A)"
    )
    masked_imei = models.CharField(
        max_length=30, 
        blank=True, 
        default='', 
        help_text="Optional masked IMEI"
    )

    # Configurable Quality Inspection Checklist
    display_inspection = models.CharField(
        max_length=80, 
        choices=OK_NOT_OK_CHOICES,
        default="OK", 
        blank=True, 
        help_text="Display inspection status"
    )
    truetone_inspection = models.CharField(
        max_length=80, 
        choices=OK_NOT_OK_CHOICES,
        default="OK", 
        blank=True, 
        help_text="TrueTone status"
    )
    faceid_inspection = models.CharField(
        max_length=80, 
        choices=WORKING_CHOICES,
        default="Working", 
        blank=True, 
        help_text="FaceID & sensors status"
    )
    sound_inspection = models.CharField(
        max_length=80, 
        choices=OK_NOT_OK_CHOICES,
        default="OK", 
        blank=True, 
        help_text="Sound and speaker status"
    )
    charging_inspection = models.CharField(
        max_length=80, 
        choices=OK_NOT_OK_CHOICES,
        default="OK", 
        blank=True, 
        help_text="Charging port status"
    )
    camera_inspection = models.CharField(
        max_length=80, 
        choices=OK_NOT_OK_CHOICES,
        default="OK", 
        blank=True, 
        help_text="Camera lens and focus status"
    )
    camera_portrait = models.CharField(
        max_length=30,
        choices=QUALITY_GRADE_CHOICES,
        default="Perfect",
        blank=True,
        help_text="Camera Portrait quality"
    )
    midframe_fitting = models.CharField(
        max_length=30,
        choices=QUALITY_GRADE_CHOICES,
        default="Perfect",
        blank=True,
        help_text="Midframe fitting quality"
    )
    lens_freshness = models.CharField(
        max_length=30,
        choices=QUALITY_GRADE_CHOICES,
        default="Perfect",
        blank=True,
        help_text="Lens freshness quality"
    )
    flashlight_inspection = models.CharField(
        max_length=80, 
        choices=OK_NOT_OK_CHOICES,
        default="OK", 
        blank=True, 
        help_text="Flashlight status"
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
        help_text="Device history, inspection test report summary."
    )
    description_bn = models.TextField(blank=True, help_text="বাংলা বিবরণ")

    primary_image = models.ImageField(upload_to='products/', blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')
    featured = models.BooleanField(default=False, help_text="Feature on Homepage")
    warranty_info = models.CharField(
        max_length=150, 
        blank=True,
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
        clean_model = self.model.name.replace('iPhone ', '').replace(' ', '')
        if not self.sku:
            rand_code = uuid.uuid4().hex[:4].upper()
            self.sku = f"GD-{clean_model}-{rand_code}"
        elif not self.sku.startswith(f"GD-{clean_model}") and self.sku.startswith("GD-"):
            # Model changed: update the SKU prefix while keeping or generating unique suffix
            parts = self.sku.split('-')
            suffix = parts[-1] if len(parts) > 1 else uuid.uuid4().hex[:4].upper()
            new_sku = f"GD-{clean_model}-{suffix}"
            if Product.objects.filter(sku=new_sku).exclude(id=self.id).exists():
                new_sku = f"GD-{clean_model}-{uuid.uuid4().hex[:4].upper()}"
            self.sku = new_sku
        
        if not self.slug or (self.model and slugify(self.model.name) not in self.slug):
            base_slug = slugify(f"{self.model.name}-{self.storage}-{self.color}-{self.sku}")
            if Product.objects.filter(slug=base_slug).exclude(id=self.id).exists():
                base_slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
            self.slug = base_slug

        # Process / convert HEIC/HEIF primary image
        if self.primary_image and hasattr(self.primary_image, 'file'):
            name = getattr(self.primary_image, 'name', '')
            if name.lower().endswith(('.heic', '.heif', '.png', '.jpeg', '.jpg', '.webp')):
                # Only re-process if it's an uploaded file object
                if hasattr(self.primary_image.file, 'content_type') or name.lower().endswith(('.heic', '.heif')):
                    from .image_utils import process_image_file
                    converted = process_image_file(self.primary_image)
                    if converted:
                        self.primary_image = converted
            
        super().save(*args, **kwargs)

    @property
    def primary_image_url(self):
        """
        Safely returns the primary image URL or empty string if file or storage is missing or misconfigured.
        Guarantees template rendering will never crash with ValueError.
        """
        if not self.primary_image:
            return ""
        try:
            return self.primary_image.url
        except Exception:
            return ""

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    @property
    def is_in_stock(self):
        return self.status == 'available'

    @property
    def discount_amount(self):
        if self.original_price and self.original_price > self.price:
            return self.original_price - self.price
        return 0

    @property
    def inspection_checklist(self):
        def format_item(label, val):
            if not val:
                return ""
            if ":" in val:
                return val
            return f"{label}: {val}"

        items = [
            format_item("Display / Refresh Rate", self.display_inspection),
            format_item("TrueTone", self.truetone_inspection),
            format_item("FaceID & Sensors", self.faceid_inspection),
            format_item("Sound & Vibration", self.sound_inspection),
            format_item("Charging Port & Battery", self.charging_inspection),
            format_item("Camera (Front & Back)", self.camera_inspection),
            format_item("Camera Portrait", self.camera_portrait),
            format_item("Midframe Fitting", self.midframe_fitting),
            format_item("Lens Freshness", self.lens_freshness),
            format_item("Flashlight / Torch", self.flashlight_inspection),
        ]
        return [item.strip() for item in items if item and item.strip()]

    @property
    def condition_display_bn(self):
        if self.condition == 'like_new':
            return '৯৯%+ নতুন'
        elif self.condition == 'excellent':
            return '৯৫%+ নতুন'
        return '৯০%+ নতুন'


    @property
    def sim_display_bn(self):
        if self.sim_type == 'physical_esim':
            return '১ ফিজিক্যাল সিম + ১ ই-সিম'
        elif self.sim_type == 'dual_esim':
            return 'ডুয়াল ই-সিম (USA ভ্যারিয়েন্ট)'
        elif self.sim_type == 'wifi_only':
            return 'ওয়াইফাই অনলি (WiFi Only)'
        return 'ডুয়াল ফিজিক্যাল সিম (HK/China)'

    @property
    def approved_reviews(self):
        return self.reviews.filter(is_approved=True).order_by('-created_at')

    @property
    def average_rating(self):
        reviews = self.approved_reviews
        if not reviews.exists():
            return 5.0
        total = sum(r.rating for r in reviews)
        return round(total / reviews.count(), 1)

    @property
    def review_count(self):
        return self.approved_reviews.count()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=150, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Product Image"
        verbose_name_plural = "Product Gallery Images"

    @property
    def image_url(self):
        """
        Safely returns the gallery image URL or empty string if file or storage is missing or misconfigured.
        """
        if not self.image:
            return ""
        try:
            return self.image.url
        except Exception:
            return ""

    def __str__(self):
        return f"Image for {self.product.sku}"

    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'file'):
            name = getattr(self.image, 'name', '')
            if name.lower().endswith(('.heic', '.heif', '.png', '.jpeg', '.jpg', '.webp')):
                if hasattr(self.image.file, 'content_type') or name.lower().endswith(('.heic', '.heif')):
                    from .image_utils import process_image_file
                    converted = process_image_file(self.image)
                    if converted:
                        self.image = converted
        super().save(*args, **kwargs)


class Review(models.Model):
    RATING_CHOICES = [
        (5, '5 Stars - Excellent'),
        (4, '4 Stars - Very Good'),
        (3, '3 Stars - Average'),
        (2, '2 Stars - Below Average'),
        (1, '1 Star - Poor'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_email = models.EmailField(blank=True)
    rating = models.PositiveSmallIntegerField(default=5, choices=RATING_CHOICES)
    title = models.CharField(max_length=150, blank=True)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return f"{self.customer_name} ({self.rating}★) on {self.product.sku}"



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
    
    phone_number = models.CharField(max_length=30, default="+8801406169818")
    whatsapp_number = models.CharField(max_length=30, default="+8801406169818")
    email = models.EmailField(default="gadgetdeluxe0@gmail.com")
    address_en = models.CharField(max_length=255, default="875, East Shewrapara, Shewrapara Metro Station, Kafrul, Dhaka")
    address_bn = models.CharField(max_length=255, default="৮৭৫, পূর্ব শেওড়াপাড়া, শেওড়াপাড়া মেট্রো স্টেশন, কাফরুল, ঢাকা")

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
