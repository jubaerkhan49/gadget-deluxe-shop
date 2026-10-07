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
        # Visiting public homepage should record PageVisit
        self.client.get(reverse('store:home'))
        self.assertTrue(PageVisit.objects.filter(path=reverse('store:home')).exists())
