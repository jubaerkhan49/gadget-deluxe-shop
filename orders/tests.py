from django.test import TestCase, Client
from django.urls import reverse
from store.models import IPhoneModel, Product, StoreSettings
from orders.models import Order, OrderItem
from decimal import Decimal


class OrderFlowTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.settings = StoreSettings.get_settings()
        self.settings.delivery_charge_inside_dhaka = Decimal(100)
        self.settings.delivery_charge_outside_dhaka = Decimal(150)
        self.settings.save()

        self.model = IPhoneModel.objects.create(name="iPhone 16 Pro Max", slug="iphone-16-pro-max", release_year=2024)
        self.product = Product.objects.create(
            title="iPhone 16 Pro Max 256GB Desert Titanium",
            model=self.model,
            storage="256GB",
            color="Desert Titanium",
            condition="like_new",
            battery_health=100,
            sim_type="dual_esim",
            price=Decimal(145000),
            status="available"
        )

    def test_cart_add_and_view(self):
        add_url = reverse('orders:cart_add', kwargs={'product_id': self.product.id})
        response = self.client.post(add_url)
        self.assertEqual(response.status_code, 302)

        cart_url = reverse('orders:cart_detail')
        cart_res = self.client.get(cart_url)
        self.assertEqual(cart_res.status_code, 200)
        self.assertContains(cart_res, "iPhone 16 Pro Max")
        self.assertContains(cart_res, "145000")

    def test_buy_now_direct_checkout_without_cart_message(self):
        add_url = reverse('orders:cart_add', kwargs={'product_id': self.product.id})
        response = self.client.post(add_url, {'buy_now': '1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        # Should redirect directly to checkout
        self.assertIn('/orders/checkout/', response.redirect_chain[0][0])
        # Ensure 'Added ... to your cart' message is NOT displayed
        self.assertNotContains(response, "to your cart.")

    def test_guest_checkout_flow(self):
        # 1. Add product to cart
        self.client.post(reverse('orders:cart_add', kwargs={'product_id': self.product.id}))

        # 2. Submit checkout form
        checkout_url = reverse('orders:checkout')
        post_data = {
            'full_name': 'Hasan Mahmud',
            'phone': '01712345678',
            'email': 'hasan@example.com',
            'delivery_address': 'Flat 4B, House 12, Road 5, Dhanmondi',
            'city': 'inside_dhaka',
            'delivery_notes': 'Please call before arriving',
            'payment_method': 'bank_transfer',
            'payment_sender_number': '01712345678',
            'payment_trx_id': '9J4K2L8M1N',
        }
        response = self.client.post(checkout_url, post_data)
        self.assertEqual(response.status_code, 302)

        # 3. Check Order created in DB
        order = Order.objects.get(phone='01712345678')
        self.assertEqual(order.full_name, 'Hasan Mahmud')
        self.assertEqual(order.subtotal, Decimal(145000))
        self.assertEqual(order.delivery_charge, Decimal(100))
        self.assertEqual(order.total_amount, Decimal(145100))
        self.assertEqual(order.payment_method, 'bank_transfer')
        self.assertEqual(order.payment_trx_id, '9J4K2L8M1N')
        self.assertEqual(order.payment_status, 'pending_verification')
        self.assertEqual(order.order_status, 'pending')

        # 4. Check product stock marked as reserved
        self.product.refresh_from_db()
        self.assertEqual(self.product.status, 'reserved')

        # 5. Check Order Tracking page
        track_url = reverse('orders:track_order') + f"?order_number={order.order_number}&phone=01712345678"
        track_res = self.client.get(track_url)
        self.assertEqual(track_res.status_code, 200)
        self.assertContains(track_res, order.order_number)
        self.assertContains(track_res, "Placed")
