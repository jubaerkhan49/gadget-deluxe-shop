from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import IPhoneModel, Product, FAQ, StoreSettings
from orders.models import Order, OrderItem
from dashboard.models import PageVisit
from decimal import Decimal


class DashboardTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser('boss', 'boss@gadgetdeluxe.shop', 'BossPass123!')
        self.customer = User.objects.create_user('john', 'john@example.com', 'JohnPass123!')

        self.model = IPhoneModel.objects.create(name="iPhone 15 Pro Max", slug="iphone-15-pro-max", release_year=2023)
        self.product = Product.objects.create(
            title="iPhone 15 Pro Max 256GB Blue Titanium",
            model=self.model,
            storage="256GB",
            color="Blue Titanium",
            condition="like_new",
            battery_health=95,
            sim_type="physical_esim",
            price=Decimal(115000),
            status="available"
        )
        self.order = Order.objects.create(
            full_name="Abir Hasan",
            phone="01799887766",
            delivery_address="Banani, Dhaka",
            city="inside_dhaka",
            payment_method="bkash",
            payment_sender_number="01799887766",
            payment_trx_id="8BKASH9928",
            payment_status="pending_verification",
            order_status="pending",
            subtotal=Decimal(115000),
            delivery_charge=Decimal(100),
            total_amount=Decimal(115100)
        )
        self.faq = FAQ.objects.create(
            category="quality",
            question_en="Is FaceID tested?",
            question_bn="ফেস আইডি টেস্ট করা হয়েছে?",
            answer_en="Yes, 100% working.",
            answer_bn="হ্যাঁ, ১০০% সচল।"
        )

    def test_anonymous_access_denied(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)

    def test_admin_dashboard_home(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard Overview")
        self.assertContains(response, "Gross Sales")
        self.assertContains(response, "115100")

    def test_analytics_view(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:analytics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Traffic & Cash Flow Analytics")
        self.assertContains(response, "Payment Method Cash Flow Share")

    def test_orders_list_and_detail(self):
        self.client.force_login(self.admin_user)
        # Order list
        res = self.client.get(reverse('dashboard:order_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.order.order_number)

        # Order detail
        detail_res = self.client.get(reverse('dashboard:order_detail', kwargs={'order_id': self.order.id}))
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, "8BKASH9928")

        # Update order status
        post_res = self.client.post(reverse('dashboard:order_detail', kwargs={'order_id': self.order.id}), {
            'order_status': 'confirmed',
            'payment_status': 'paid'
        })
        self.assertEqual(post_res.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.order_status, 'confirmed')
        self.assertEqual(self.order.payment_status, 'paid')

    def test_order_export_csv(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('dashboard:order_export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertContains(response, self.order.order_number)

    def test_product_crud(self):
        self.client.force_login(self.admin_user)
        # Create product
        post_data = {
            'model': self.model.id,
            'title': 'iPhone 15 Pro Max 512GB White Titanium',
            'title_bn': 'হোয়াইট টাইটানিয়াম',
            'storage': '512GB',
            'color': 'White Titanium',
            'color_bn': 'হোয়াইট টাইটানিয়াম',
            'condition': 'like_new',
            'battery_health': 99,
            'cycle_count': 45,
            'sim_type': 'dual_esim',
            'price': 125000,
            'status': 'available',
        }
        res = self.client.post(reverse('dashboard:product_create'), post_data)
        self.assertEqual(res.status_code, 302)
        created_p = Product.objects.filter(title='iPhone 15 Pro Max 512GB White Titanium').first()
        self.assertIsNotNone(created_p)
        self.assertEqual(created_p.cycle_count, 45)

        # Delete product
        del_res = self.client.post(reverse('dashboard:product_delete', kwargs={'product_id': created_p.id}))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(Product.objects.filter(id=created_p.id).exists())

        # Toggle status
        toggle_res = self.client.get(reverse('dashboard:product_toggle_status', kwargs={'product_id': self.product.id, 'new_status': 'sold'}))
        self.assertEqual(toggle_res.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.status, 'sold')

    def test_product_heic_upload_crud(self):
        import io
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        import pillow_heif
        pillow_heif.register_heif_opener()

        self.client.force_login(self.admin_user)
        buf = io.BytesIO()
        img = Image.new('RGB', (100, 100), color='purple')
        img.save(buf, format='HEIF')
        buf.seek(0)
        heic_file = SimpleUploadedFile('iphone_15_photo.HEIC', buf.read(), content_type='image/heic')

        post_data = {
            'model': self.model.id,
            'title': 'iPhone 15 Pro Max 256GB Purple HEIC',
            'storage': '256GB',
            'color': 'Purple',
            'condition': 'like_new',
            'battery_health': 97,
            'cycle_count': 12,
            'sim_type': 'wifi_only',
            'price': 118000,
            'status': 'available',
            'primary_image': heic_file,
        }
        res = self.client.post(reverse('dashboard:product_create'), post_data)
        self.assertEqual(res.status_code, 302)
        created_p = Product.objects.filter(title='iPhone 15 Pro Max 256GB Purple HEIC').first()
        self.assertIsNotNone(created_p)
        self.assertTrue(created_p.primary_image.name.endswith('.jpg'))

    def test_faq_crud(self):
        self.client.force_login(self.admin_user)
        post_data = {
            'category': 'battery',
            'question_en': 'How long does battery last?',
            'question_bn': 'ব্যাটারি ব্যাকআপ কতক্ষণ?',
            'answer_en': 'All day battery backup.',
            'answer_bn': 'সারাদিন ব্যাকআপ পাওয়া যায়।',
            'order': 5,
            'is_active': True,
        }
        create_res = self.client.post(reverse('dashboard:faq_create'), post_data)
        self.assertEqual(create_res.status_code, 302)
        self.assertTrue(FAQ.objects.filter(question_en='How long does battery last?').exists())

    def test_store_settings_update(self):
        self.client.force_login(self.admin_user)
        post_data = {
            'store_name': 'Gadget Deluxe Official',
            'tagline_en': 'Top Used iPhones in BD',
            'tagline_bn': 'সেরা ব্যবহৃত আইফোন',
            'phone_number': '+8801999888777',
            'whatsapp_number': '+8801999888777',
            'email': 'support@gadgetdeluxe.shop',
            'address_en': 'Bashundhara City, Dhaka',
            'address_bn': 'বসুন্ধরা সিটি, ঢাকা',
            'delivery_charge_inside_dhaka': 120,
            'delivery_charge_outside_dhaka': 160,
            'warranty_badge_en': '7 Days Full Replacement',
            'warranty_badge_bn': '৭ দিনের গ্যারান্টি',
            'bkash_number': '01999888777 (Merchant)',
            'bkash_instructions_en': 'Make payment to merchant',
            'bkash_instructions_bn': 'পেমেন্ট করুন',
            'nagad_number': '01999888777',
            'nagad_instructions_en': 'Send money',
            'nagad_instructions_bn': 'সেন্ড মানি করুন',
            'rocket_number': '01999888777-1',
            'rocket_instructions_en': 'Send money',
            'rocket_instructions_bn': 'সেন্ড মানি করুন',
            'bank_details_en': 'City Bank A/C 12345',
            'bank_details_bn': 'সিটি ব্যাংক',
        }
        res = self.client.post(reverse('dashboard:settings'), post_data)
        self.assertEqual(res.status_code, 302)
        settings = StoreSettings.get_settings()
        self.assertEqual(settings.store_name, 'Gadget Deluxe Official')
        self.assertEqual(settings.delivery_charge_inside_dhaka, Decimal(120))

    def test_visitor_tracking_middleware(self):
        # 1. Visiting public homepage as anonymous user should record PageVisit
        self.client.get(reverse('store:home'))
        self.assertTrue(PageVisit.objects.filter(path=reverse('store:home')).exists())
        initial_count = PageVisit.objects.count()

        # 2. Staff user visits should NOT increment PageVisit count
        self.client.force_login(self.admin_user)
        self.client.get(reverse('store:home'))
        self.assertEqual(PageVisit.objects.count(), initial_count)

        # 3. Bot visits should NOT be recorded
        self.client.logout()
        self.client.get(reverse('store:home'), HTTP_USER_AGENT='Googlebot/2.1 (+http://www.google.com/bot.html)')
        self.assertEqual(PageVisit.objects.count(), initial_count)

    def test_customer_list_and_detail(self):
        from store.models import Review
        self.client.force_login(self.admin_user)
        
        # Create an OrderItem and Review for the customer
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_title=self.product.title,
            product_sku=self.product.sku,
            product_model=self.product.model.name,
            product_storage=self.product.storage,
            product_color=self.product.color,
            product_condition=self.product.condition,
            product_battery_health=self.product.battery_health,
            price=self.product.price,
            quantity=1
        )
        Review.objects.create(
            product=self.product,
            customer_name="Abir Hasan",
            customer_phone="01799887766",
            rating=5,
            title="Awesome phone",
            comment="Excellent condition, highly recommend!",
            is_approved=True
        )

        # 1. Customer Directory List
        list_res = self.client.get(reverse('dashboard:customer_list'))
        self.assertEqual(list_res.status_code, 200)
        self.assertContains(list_res, "Abir Hasan")
        self.assertContains(list_res, "01799887766")
        self.assertContains(list_res, "Total Customer Spend")

        # Search filter
        search_res = self.client.get(reverse('dashboard:customer_list') + '?q=Abir')
        self.assertEqual(search_res.status_code, 200)
        self.assertContains(search_res, "Abir Hasan")

        # 2. Customer Detail
        detail_res = self.client.get(reverse('dashboard:customer_detail', kwargs={'customer_key': 'p-01799887766'}))
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, "Abir Hasan")
        self.assertContains(detail_res, "Purchased iPhone Devices")
        self.assertContains(detail_res, self.product.title)
        self.assertContains(detail_res, "Awesome phone")

    def test_review_moderation(self):
        from store.models import Review
        self.client.force_login(self.admin_user)
        
        rev = Review.objects.create(
            product=self.product,
            customer_name="Tanvir Rahman",
            customer_phone="01611223344",
            rating=4,
            title="Good device",
            comment="Works as described.",
            is_approved=True
        )

        # 1. Review List
        res = self.client.get(reverse('dashboard:review_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Tanvir Rahman")
        self.assertContains(res, "Good device")

        # 2. Toggle Approval (Hide)
        toggle_res = self.client.get(reverse('dashboard:review_toggle_approval', kwargs={'review_id': rev.id}))
        self.assertEqual(toggle_res.status_code, 302)
        rev.refresh_from_db()
        self.assertFalse(rev.is_approved)

        # 3. Delete Review
        del_res = self.client.get(reverse('dashboard:review_delete', kwargs={'review_id': rev.id}))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(Review.objects.filter(id=rev.id).exists())

    def test_admin_login_page_redesign(self):
        """Verify redesigned admin login page renders successfully with luxury branding"""
        res = self.client.get(reverse('admin:login'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Gadget Deluxe")
        self.assertContains(res, "Staff Administration")
        self.assertContains(res, "id_username")
        self.assertContains(res, "id_password")
        self.assertContains(res, "togglePasswordBtn")
        self.assertTemplateUsed(res, 'admin/login.html')

    def test_admin_login_redirects_to_shop_admin(self):
        """Staff admin login should redirect directly to /shop-admin/"""
        # When already logged in as staff and accessing admin login:
        self.client.force_login(self.admin_user)
        res = self.client.get(reverse('admin:login'))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse('dashboard:home'))

    def test_change_credentials_flow_with_otp(self):
        """Test staff can send OTP and update username, email, and password with OTP verification"""
        self.client.force_login(self.admin_user)
        # 1. GET page
        res = self.client.get(reverse('dashboard:change_password'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Admin Credentials & Security")
        self.assertContains(res, "id_username")
        self.assertContains(res, "id_email")
        self.assertContains(res, "id_otp")

        # 2. Request OTP via AJAX POST - must be sent to current email
        otp_res = self.client.post(reverse('dashboard:send_admin_otp'), data={'email': 'anyother@example.com'})
        self.assertEqual(otp_res.status_code, 200)
        otp_data = otp_res.json()
        self.assertTrue(otp_data['success'])
        self.assertEqual(otp_data['current_email'], self.admin_user.email)
        
        # Verify OTP is stored in session for current email
        session = self.client.session
        self.assertIn('admin_otp', session)
        self.assertEqual(session['admin_otp']['email'], self.admin_user.email)
        generated_otp = session['admin_otp']['code']

        # 3. Submit credentials update with invalid OTP -> should fail
        fail_data = {
            'username': 'superboss',
            'email': 'newboss@gadgetdeluxe.shop',
            'current_password': 'BossPass123!',
            'new_password': 'NewSecurePass2026!#',
            'confirm_password': 'NewSecurePass2026!#',
            'otp': '999999',
        }
        fail_res = self.client.post(reverse('dashboard:change_password'), data=fail_data)
        self.assertEqual(fail_res.status_code, 200)
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.username, 'boss')  # unchanged

        # 4. Submit credentials update with valid OTP -> should succeed
        success_data = {
            'username': 'superboss',
            'email': 'newboss@gadgetdeluxe.shop',
            'current_password': 'BossPass123!',
            'new_password': 'NewSecurePass2026!#',
            'confirm_password': 'NewSecurePass2026!#',
            'otp': generated_otp,
        }
        success_res = self.client.post(reverse('dashboard:change_password'), data=success_data)
        self.assertEqual(success_res.status_code, 302)
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.username, 'superboss')
        self.assertEqual(self.admin_user.email, 'newboss@gadgetdeluxe.shop')
        self.assertTrue(self.admin_user.check_password('NewSecurePass2026!#'))
        
        # Verify OTP is cleared after use
        self.assertNotIn('admin_otp', self.client.session)

    def test_product_form_photo_preview_markup(self):
        """Ensure photo preview cards, gallery uploader, and scripts are present in product form"""
        self.client.force_login(self.admin_user)
        res = self.client.get(reverse('dashboard:product_edit', kwargs={'product_id': self.product.id}))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "primaryImagePreviewCard")
        self.assertContains(res, "galleryLivePreviewContainer")
        self.assertContains(res, "heic2any")



