from django.test import TestCase, Client
from django.urls import reverse
from store.models import IPhoneModel, Product, FAQ, StoreSettings
from orders.models import Order, OrderItem
from decimal import Decimal


class StoreViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.model = IPhoneModel.objects.create(name="iPhone 15 Pro", slug="iphone-15-pro", release_year=2023)
        self.product = Product.objects.create(
            title="iPhone 15 Pro 256GB Natural Titanium",
            model=self.model,
            storage="256GB",
            color="Natural Titanium",
            condition="like_new",
            battery_health=98,
            sim_type="physical_esim",
            price=Decimal(98000),
            status="available"
        )
        self.faq = FAQ.objects.create(
            category="quality",
            question_en="Is this phone original?",
            question_bn="ফোনটি কি অরিজিনাল?",
            answer_en="Yes 100% original.",
            answer_bn="হ্যাঁ শতভাগ আসল।"
        )

    def test_homepage_loads(self):
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gadget Deluxe")
        self.assertContains(response, "iPhone 15 Pro")

    def test_product_list_filter(self):
        response = self.client.get(reverse('store:product_list') + '?model=iphone-15-pro')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "iPhone 15 Pro")

    def test_product_detail_page(self):
        self.product.original_price = Decimal(105000)
        self.product.display_inspection = "120Hz ProMotion OLED: OK"
        self.product.save()
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Natural Titanium")
        self.assertContains(response, "98%")
        self.assertContains(response, "120Hz ProMotion OLED: OK")
        self.assertContains(response, "Save ৳7000")
        self.assertContains(response, "Buy Now")

    def test_heic_image_conversion(self):
        import io
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        from store.image_utils import process_image_file

        buf = io.BytesIO()
        img = Image.new('RGB', (120, 120), color='blue')
        img.save(buf, format='JPEG')
        buf.seek(0)
        uploaded = SimpleUploadedFile('sample_iphone.HEIC', buf.read(), content_type='image/heic')
        converted = process_image_file(uploaded)
        self.assertTrue(converted.name.endswith('.jpg'))

    def test_faq_page(self):
        response = self.client.get(reverse('store:faq'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Is this phone original?")

    def test_language_switch(self):
        response = self.client.get(reverse('store:switch_language', kwargs={'lang_code': 'bn'}))
        self.assertEqual(response.status_code, 302)
        # Check session and cookie
        self.assertEqual(self.client.session.get('_language'), 'bn')
