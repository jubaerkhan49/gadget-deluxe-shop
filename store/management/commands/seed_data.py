from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from store.models import IPhoneModel, Product, FAQ, StoreSettings, ProductImage
from decimal import Decimal
import io
from PIL import Image, ImageDraw, ImageFont


def generate_iphone_mockup(model_name, color_name, bg_hex):
    """
    Generate a clean, high-resolution aesthetic iPhone illustration for product cards.
    """
    width, height = 600, 800
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    # Convert hex color to rgb
    hex_clean = bg_hex.lstrip('#')
    phone_color = tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))
    
    # Outer body (rounded rectangle)
    body_bbox = [130, 80, 470, 720]
    draw.rounded_rectangle(body_bbox, radius=55, fill=phone_color, outline=(40, 40, 40), width=4)
    
    # Inner display bezel
    screen_bbox = [144, 94, 456, 706]
    draw.rounded_rectangle(screen_bbox, radius=46, fill=(10, 10, 15), outline=(30, 30, 30), width=2)

    # Dynamic Island pill
    pill_bbox = [245, 110, 355, 135]
    draw.rounded_rectangle(pill_bbox, radius=12, fill=(0, 0, 0))
    # Camera sensor dot
    draw.ellipse([335, 118, 345, 128], fill=(20, 20, 40))

    # Wallpaper gradient / glow inside screen
    glow_bbox = [180, 240, 420, 480]
    draw.ellipse(glow_bbox, fill=(phone_color[0]//2, phone_color[1]//2, phone_color[2]//2, 100))

    # Apple logo outline / text in screen center
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    draw.text((300, 380), model_name, fill=(240, 240, 245), anchor="mm")
    draw.text((300, 410), color_name, fill=(160, 160, 170), anchor="mm")
    draw.text((300, 650), "Gadget Deluxe", fill=(100, 100, 110), anchor="mm")

    # Triple Camera bump on back reflection or subtle accent lines
    draw.arc([135, 85, 465, 715], start=0, end=90, fill=(255, 255, 255, 80), width=3)

    img_io = io.BytesIO()
    image.save(img_io, format='PNG')
    return ContentFile(img_io.getvalue(), name=f"{model_name.lower().replace(' ', '_')}_{color_name.lower().replace(' ', '_')}.png")


class Command(BaseCommand):
    help = 'Seeds database with realistic iPhone 14/15/16 Pro listings, FAQs, and Store Settings'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Gadget Deluxe database..."))

        # 1. Superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@gadgetdeluxe.shop', 'admin123456')
            self.stdout.write(self.style.SUCCESS("Created superuser: admin / admin123456"))

        # 2. Store Settings
        settings = StoreSettings.get_settings()
        settings.store_name = "Gadget Deluxe"
        settings.tagline_en = "Quality Used iPhones, Carefully Checked."
        settings.tagline_bn = "যাচাইকৃত প্রিমিয়াম ব্যবহৃত আইফোন।"
        settings.phone_number = "+8801406169818"
        settings.whatsapp_number = "+8801406169818"
        settings.email = "gadgetdeluxe0@gmail.com"
        settings.address_en = "875, East Shewrapara, Shewrapara Metro Station, Kafrul, Dhaka"
        settings.address_bn = "৮৭৫, পূর্ব শেওড়াপাড়া, শেওড়াপাড়া মেট্রো স্টেশন, কাফরুল, ঢাকা"
        settings.bkash_number = "01711223344 (Personal / Send Money)"
        settings.nagad_number = "01711223344 (Personal / Send Money)"
        settings.rocket_number = "01711223344-8 (Personal)"
        settings.bank_details_en = "Bank: The City Bank Limited\nAccount Name: Gadget Deluxe Shop\nAccount Number: 1501209847001\nBranch: Kawran Bazar / Bashundhara Branch\nRouting Number: 225271890"
        settings.bank_details_bn = "ব্যাংক: দ্য সিটি ব্যাংক লিমিটেড\nহিসাবের নাম: গ্যাজেট ডিলাক্স শপ\nহিসাব নম্বর: 1501209847001\nশাখা: কাওরান বাজার / বসুন্ধরা শাখা"
        settings.delivery_charge_inside_dhaka = Decimal(100)
        settings.delivery_charge_outside_dhaka = Decimal(150)
        settings.save()

        # 3. iPhone Models (Exclusively 14 Pro, 14 Pro Max, 15 Pro, 15 Pro Max, 16 Pro, 16 Pro Max)
        models_data = [
            ('iPhone 16 Pro Max', 2024, 1),
            ('iPhone 16 Pro', 2024, 2),
            ('iPhone 15 Pro Max', 2023, 3),
            ('iPhone 15 Pro', 2023, 4),
            ('iPhone 14 Pro Max', 2022, 5),
            ('iPhone 14 Pro', 2022, 6),
        ]

        model_objs = {}
        for name, year, order in models_data:
            obj, _ = IPhoneModel.objects.get_or_create(
                name=name,
                defaults={'release_year': year, 'order': order, 'is_active': True}
            )
            model_objs[name] = obj

        # 4. Realistic iPhone Listings
        listings = [
            {
                'model': 'iPhone 16 Pro Max',
                'storage': '256GB',
                'color': 'Desert Titanium',
                'color_bn': 'ডেজার্ট টাইটানিয়াম',
                'color_hex': '#c4b5a5',
                'condition': 'like_new',
                'battery_health': 100,
                'sim_type': 'dual_esim',
                'origin_region': 'USA (LL/A)',
                'price': Decimal(145000),
                'original_price': Decimal(152000),
                'description': 'Pristine 100% like new iPhone 16 Pro Max Desert Titanium. 3uTools score 100%. Flawless Grade A++ unit with original factory packaging and cable.',
                'description_bn': '১০০% লাইক নিউ কন্ডিশন ডেজার্ট টাইটানিয়াম আইফোন ১৬ প্রো ম্যাক্স। ৩ইউ-টুলস স্কোর ১০০%, সব পার্টস অরিজিনাল। সাথে অরিজিনাল ক্যাবল রয়েছে।',
                'featured': True,
            },
            {
                'model': 'iPhone 16 Pro',
                'storage': '128GB',
                'color': 'Natural Titanium',
                'color_bn': 'ন্যাচারাল টাইটানিয়াম',
                'color_hex': '#9e9e98',
                'condition': 'like_new',
                'battery_health': 100,
                'sim_type': 'physical_esim',
                'origin_region': 'Singapore (ZP/A)',
                'price': Decimal(128000),
                'original_price': Decimal(135000),
                'description': 'iPhone 16 Pro 128GB Natural Titanium. Physical SIM + eSIM. Battery health 100%. Pristine body without a single scratch.',
                'description_bn': 'ন্যাচারাল টাইটানিয়াম ১৬ প্রো ১২৮জিবি। ১টি ফিজিক্যাল ও ১টি ই-সিম। ব্যাটারি ১০০%। সম্পুর্ণ ফ্রেশ ও ত্রুটিমুক্ত।',
                'featured': True,
            },
            {
                'model': 'iPhone 15 Pro Max',
                'storage': '256GB',
                'color': 'Natural Titanium',
                'color_bn': 'ন্যাচারাল টাইটানিয়াম',
                'color_hex': '#a29e97',
                'condition': 'like_new',
                'battery_health': 97,
                'sim_type': 'physical_esim',
                'origin_region': 'Japan (J/A)',
                'price': Decimal(109000),
                'original_price': Decimal(115000),
                'description': 'iPhone 15 Pro Max 256GB in pristine condition. Titanium finish, 97% authentic battery health. Tested TrueTone, Action Button & 5x Optical Zoom.',
                'description_bn': 'আইফোন ১৫ প্রো ম্যাক্স ২৫৬জিবি ন্যাচারাল টাইটানিয়াম। ৯৭% অথেনটিক ব্যাটারি হেলথ। ট্রুটোন ও ৫এক্স জুম ১০০% সচল।',
                'featured': True,
            },
            {
                'model': 'iPhone 15 Pro Max',
                'storage': '512GB',
                'color': 'Blue Titanium',
                'color_bn': 'ব্লু টাইটানিয়াম',
                'color_hex': '#3b444b',
                'condition': 'excellent',
                'battery_health': 94,
                'sim_type': 'dual_physical',
                'origin_region': 'Hong Kong (ZA/A)',
                'price': Decimal(116000),
                'original_price': Decimal(122000),
                'description': 'Dual physical SIM variant from Hong Kong. Huge 512GB storage. 94% original battery health. Excellent condition with minor glass protector usage.',
                'description_bn': 'ডুয়াল ফিজিক্যাল সিম ভ্যারিয়েন্ট (হংকং)। ৫১২জিবি হিউজ স্টোরেজ। ৯৪% ব্যাটারি হেলথ।',
                'featured': True,
            },
            {
                'model': 'iPhone 15 Pro',
                'storage': '128GB',
                'color': 'Black Titanium',
                'color_bn': 'ব্ল্যাক টাইটানিয়াম',
                'color_hex': '#2c2c2e',
                'condition': 'like_new',
                'battery_health': 96,
                'sim_type': 'physical_esim',
                'origin_region': 'USA (LL/A)',
                'price': Decimal(92000),
                'original_price': Decimal(98000),
                'description': 'Compact powerhouse iPhone 15 Pro 128GB Black Titanium. 96% battery health, spotless screen and camera rings. Full 52-point check passed.',
                'description_bn': 'আইফোন ১৫ প্রো ১২৮জিবি ব্ল্যাক টাইটানিয়াম। ৯৬% ব্যাটারি হেলথ। ক্যামেরা ও স্ক্রিন সম্পূর্ণ ফ্রেশ।',
                'featured': True,
            },
            {
                'model': 'iPhone 15 Pro',
                'storage': '256GB',
                'color': 'White Titanium',
                'color_bn': 'হোয়াইট টাইটানিয়াম',
                'color_hex': '#e2e2df',
                'condition': 'excellent',
                'battery_health': 91,
                'sim_type': 'dual_esim',
                'origin_region': 'USA (LL/A)',
                'price': Decimal(96000),
                'original_price': Decimal(102000),
                'description': 'White Titanium 256GB iPhone 15 Pro. 91% battery health. Super smooth 120Hz ProMotion display and fast USB-C transfer speeds.',
                'description_bn': 'হোয়াইট টাইটানিয়াম ২৫৬জিবি ১৫ প্রো। ৯১% ব্যাটারি হেলথ। টাইপ-সি পোর্ট ও ১২০ হার্টজ প্রোমোশন ডিসপ্লে।',
                'featured': False,
            },
            {
                'model': 'iPhone 14 Pro Max',
                'storage': '128GB',
                'color': 'Deep Purple',
                'color_bn': 'ডিপ পার্পল',
                'color_hex': '#4b3f54',
                'condition': 'like_new',
                'battery_health': 89,
                'sim_type': 'physical_esim',
                'origin_region': 'Global (ZP/A)',
                'price': Decimal(86000),
                'original_price': Decimal(92000),
                'description': 'Iconic Deep Purple iPhone 14 Pro Max. Dynamic Island, 48MP main camera, 89% battery health. All factory original components.',
                'description_bn': 'জনপ্রিয় ডিপ পার্পল ১৪ প্রো ম্যাক্স ১২৮জিবি। ডাইনামিক আইল্যান্ড ও ৪৮ মেগাপিক্সেল ক্যামেরা। ৮৯% ব্যাটারি হেলথ।',
                'featured': True,
            },
            {
                'model': 'iPhone 14 Pro Max',
                'storage': '256GB',
                'color': 'Space Black',
                'color_bn': 'স্পেস ব্ল্যাক',
                'color_hex': '#1f2022',
                'condition': 'excellent',
                'battery_health': 87,
                'sim_type': 'dual_esim',
                'origin_region': 'USA (LL/A)',
                'price': Decimal(89000),
                'original_price': Decimal(95000),
                'description': 'Space Black 256GB iPhone 14 Pro Max. 87% original battery. Clean stainless steel rails, TrueTone and FaceID fully tested.',
                'description_bn': 'স্পেস ব্ল্যাক ২৫৬জিবি ১৪ প্রো ম্যাক্স। ৮৭% ব্যাটারি হেলথ। ফেস আইডি ও ট্রুটোন ১০০% ভেরিফাইড।',
                'featured': False,
            },
            {
                'model': 'iPhone 14 Pro',
                'storage': '128GB',
                'color': 'Gold',
                'color_bn': 'গোল্ড',
                'color_hex': '#fae7cf',
                'condition': 'good',
                'battery_health': 85,
                'sim_type': 'physical_esim',
                'origin_region': 'Japan (J/A)',
                'price': Decimal(76000),
                'original_price': Decimal(82000),
                'description': 'Budget-friendly iPhone 14 Pro 128GB Gold. 85% battery health. Minor micro-wear on frame but 100% functional hardware.',
                'description_bn': 'বাজেট-ফ্রেন্ডলি ১৪ প্রো ১২৮জিবি গোল্ড। ৮৫% ব্যাটারি হেলথ। সব ফিচার ও ক্যামেরা নিখুঁতভাবে কাজ করে।',
                'featured': False,
            },
        ]

        for item in listings:
            m_obj = model_objs[item['model']]
            title = f"{item['model']} {item['storage']} - {item['color']} ({item['battery_health']}% Battery)"
            title_bn = f"{item['model']} {item['storage']} - {item['color_bn']} ({item['battery_health']}% ব্যাটারি)"

            prod, created = Product.objects.get_or_create(
                title=title,
                model=m_obj,
                storage=item['storage'],
                color=item['color'],
                defaults={
                    'title_bn': title_bn,
                    'color_bn': item['color_bn'],
                    'condition': item['condition'],
                    'battery_health': item['battery_health'],
                    'sim_type': item['sim_type'],
                    'origin_region': item['origin_region'],
                    'masked_imei': f"35{item['battery_health']}840291{item['battery_health']}",
                    'price': item['price'],
                    'original_price': item['original_price'],
                    'description': item['description'],
                    'description_bn': item['description_bn'],
                    'featured': item['featured'],
                    'status': 'available',
                }
            )

            # Generate aesthetic mockup image if none attached
            if not prod.primary_image:
                mock_img = generate_iphone_mockup(item['model'], item['color'], item['color_hex'])
                prod.primary_image.save(f"{prod.slug}.png", mock_img, save=True)

        self.stdout.write(self.style.SUCCESS(f"Created {len(listings)} iPhone listings."))

        # 5. FAQs
        faq_data = [
            (
                'quality',
                'Are these iPhones used or refurbished?',
                'এগুলো কি ব্যবহৃত (Used) নাকি রিফার্বিশড আইফোন?',
                'All iPhones listed at Gadget Deluxe are genuine pre-owned devices exclusively from verified sources (USA, Singapore, Japan). Each unit is individually photographed, inspected, and tested across 52 hardware checkpoints.',
                'গ্যাজেট ডিলাক্সের প্রতিটি আইফোন সরাসরি যাচাইকৃত সোর্স (ইউএসএ, সিঙ্গাপুর, জাপান) থেকে সংগৃহীত অরিজিনাল ব্যবহৃত ডিভাইস। প্রতিটি ফোন ৫২টি হার্ডওয়্যার পয়েন্টে টেস্ট করে ওয়েবসাইটে লিস্ট করা হয়।'
            ),
            (
                'quality',
                'Are the display and internal parts 100% original?',
                'ডিসপ্লে ও ভেতরের পার্টস কি ১০০% অরিজিনাল?',
                'Yes. We strictly test every phone using 3uTools and proprietary hardware diagnostics. Displays maintain original Apple OLED panels with TrueTone enabled and FaceID functioning flawlessly. We do not sell copy-display or swapped-motherboard phones.',
                'হ্যাঁ, সম্পূর্ণ অরিজিনাল। আমরা ৩ইউ-টুলস ও ল্যাব টেস্টের মাধ্যমে ট্রুটোন, ফেসআইডি ও ক্যামেরা সেন্সর যাচাই করি। কোনো কপি ডিসপ্লে বা মাদারবোর্ড চেঞ্জড ফোন আমরা বিক্রি করি না।'
            ),
            (
                'battery',
                'What does Battery Health mean and are the batteries boosted?',
                'ব্যাটারি হেলথ কি এবং ব্যাটারি কি বুস্টেড বা ফেক?',
                'Battery health shows the current maximum capacity compared to when the battery was brand new. We transparently disclose the true factory battery percentage (e.g. 88%, 95%, 100%) without any software boosting or chip tampering.',
                'ব্যাটারি হেলথ ফোনের আসল ব্যাকআপ ক্ষমতা নির্দেশ করে। আমাদের প্রতিটি ফোনে সফটওয়্যার বা চিপ দিয়ে বুস্ট না করা প্রকৃত ব্যাটারি হেলথ স্পষ্টভাবে উল্লেখ করা থাকে।'
            ),
            (
                'battery',
                'What kind of warranty is provided with used iPhones?',
                'ব্যবহৃত আইফোনে কি ধরণের ওয়ারেন্টি দেওয়া হয়?',
                'Every iPhone purchased comes with our standard 7 Days Full Hardware Replacement Guarantee and 1 Year Free Service Warranty. If any unmentioned hardware issue arises within 7 days, we replace the device.',
                'প্রতিটি ফোনের সাথে থাকে ৭ দিনের আনকন্ডিশনাল হার্ডওয়্যার রিপ্লেসমেন্ট গ্যারান্টি এবং ১ বছরের ফ্রি সার্ভিস ওয়ারেন্টি।'
            ),
            (
                'order',
                'Can I check and inspect the phone before making payment?',
                'ডেলিভারি নেওয়ার সময় ফোন চেক করে দেখার সুযোগ আছে কি?',
                'Absolutely! With our Cash on Delivery service, you can unbox and inspect the physical condition, IMEI, TrueTone, and battery health in front of the courier agent before paying the remaining balance.',
                'অবশ্যই! ক্যাশ অন ডেলিভারিতে কুরিয়ার প্রতিনিধির সামনে ফোনের কন্ডিশন, আইএমইআই, ট্রুটোন ও ব্যাটারি হেলথ চেক করে মূল্য পরিশোধ করতে পারবেন।'
            ),
            (
                'order',
                'Can I place an order without creating an account?',
                'একাউন্ট তৈরি না করেই কি অর্ডার করা যাবে?',
                'Yes! We support seamless Guest Checkout. You only need to enter your delivery address and phone number. You can track your order at any time using your Order ID and Phone Number.',
                'হ্যাঁ! একাউন্ট ছাড়াও শুধু নাম, ঠিকানা ও মোবাইল নম্বর দিয়ে গেস্ট হিসেবে সরাসরি অর্ডার করতে পারবেন এবং ট্র্যাকিং পেজ থেকে সার্বক্ষণিক স্ট্যাটাস দেখতে পারবেন।'
            ),
            (
                'payment',
                'What payment methods are supported?',
                'কি কি পেমেন্ট মাধ্যম উপলব্ধ আছে?',
                'We accept Cash on Delivery (COD), bKash, Nagad, Rocket, and direct Bank Transfer (The City Bank / BRAC Bank). For mobile financial services, simply input your Sender Number & TrxID during checkout.',
                'আমরা ক্যাশ অন ডেলিভারি (COD), বিকাশ, নগদ, রকেট এবং সরাসরি ব্যাংক ট্রান্সফার গ্রহণ করি।'
            ),
        ]

        FAQ.objects.all().delete()
        for idx, (cat, q_en, q_bn, a_en, a_bn) in enumerate(faq_data, start=1):
            FAQ.objects.create(
                category=cat,
                question_en=q_en,
                question_bn=q_bn,
                answer_en=a_en,
                answer_bn=a_bn,
                order=idx,
                is_active=True
            )
        self.stdout.write(self.style.SUCCESS(f"Created {len(faq_data)} FAQ items."))

        self.stdout.write(self.style.SUCCESS("[OK] Database seeding completed successfully!"))
