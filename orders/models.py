from django.db import models
from django.contrib.auth.models import User
from store.models import Product
import uuid
import random


class Order(models.Model):
    CITY_CHOICES = [
        ('inside_dhaka', 'Inside Dhaka (৳100) / ঢাকা সিটির ভেতরে'),
        ('outside_dhaka', 'Outside Dhaka (৳150) / ঢাকার বাইরে সারা বাংলাদেশ'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery (COD) / ক্যাশ অন ডেলিভারি'),
        ('bkash', 'bKash / বিকাশ'),
        ('nagad', 'Nagad / নগদ'),
        ('rocket', 'Rocket / রকেট'),
        ('bank_transfer', 'Bank Transfer / ব্যাংক ট্রান্সফার'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid / অপরিশোধিত'),
        ('pending_verification', 'Pending Verification / ভেরিফিকেশন অপেক্ষমান'),
        ('paid', 'Paid / পরিশোধিত'),
        ('failed', 'Failed / ব্যর্থ'),
        ('refunded', 'Refunded / রিফান্ডকৃত'),
    ]

    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending / অপেক্ষমান'),
        ('confirmed', 'Confirmed / নিশ্চিতকৃত'),
        ('processing', 'Processing / প্রসেসিং'),
        ('shipped', 'Shipped / কুরিয়ারে পাঠানো হয়েছে'),
        ('out_for_delivery', 'Out for Delivery / ডেলিভারিতে বের হয়েছে'),
        ('delivered', 'Delivered / ডেলিভারি সম্পন্ন'),
        ('cancelled', 'Cancelled / বাতিল'),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    tracking_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # Customer Details
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    delivery_address = models.TextField()
    city = models.CharField(max_length=20, choices=CITY_CHOICES, default='inside_dhaka')
    delivery_notes = models.TextField(blank=True, null=True)

    # Payment Details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    payment_sender_number = models.CharField(max_length=30, blank=True, null=True, help_text="Sender Phone or Account Number")
    payment_trx_id = models.CharField(max_length=60, blank=True, null=True, help_text="TrxID / Bank Reference / Slip No")
    payment_status = models.CharField(max_length=25, choices=PAYMENT_STATUS_CHOICES, default='unpaid')

    # Order Status
    order_status = models.CharField(max_length=25, choices=ORDER_STATUS_CHOICES, default='pending')

    # Amount breakdown
    subtotal = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    delivery_charge = models.DecimalField(max_digits=6, decimal_places=0, default=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order #{self.order_number} - {self.full_name} (৳{self.total_amount:,})"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate clean human-readable order number e.g. GD83921
            while True:
                num = f"GD{random.randint(100000, 999999)}"
                if not Order.objects.filter(order_number=num).exists():
                    self.order_number = num
                    break
        super().save(*args, **kwargs)

    @property
    def is_guest(self):
        return self.user is None

    @property
    def status_step_index(self):
        """Helper for order tracking visual progress bar (0 to 5)"""
        steps = {
            'pending': 0,
            'confirmed': 1,
            'processing': 2,
            'shipped': 3,
            'out_for_delivery': 4,
            'delivered': 5,
            'cancelled': -1,
        }
        return steps.get(self.order_status, 0)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Snapshot of product details at time of purchase
    product_title = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50, blank=True)
    product_model = models.CharField(max_length=50)
    product_storage = models.CharField(max_length=20)
    product_color = models.CharField(max_length=50)
    product_condition = models.CharField(max_length=50)
    product_battery_health = models.PositiveIntegerField(null=True, blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=0)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.product_title} x {self.quantity}"

    @property
    def total_price(self):
        return self.price * self.quantity
