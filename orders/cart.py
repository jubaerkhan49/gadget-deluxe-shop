from decimal import Decimal
from django.conf import settings
from store.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        Note: Used phones are unique, so quantity is capped at 1 per physical device listing.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
                'product_id': product.id,
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = min(quantity, 1)
        else:
            # Since individual used phones are unique, ensure max 1
            self.cart[product_id]['quantity'] = 1

        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            if 'product' in item:
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity'] 
            for item in self.cart.values()
        )

    def validate_cart(self):
        """
        Removes any items that are no longer available in stock.
        Returns a list of removed product titles if any.
        """
        removed = []
        product_ids = list(self.cart.keys())
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

        for pid_str in product_ids:
            pid = int(pid_str)
            product = products.get(pid)
            if not product or product.status != 'available':
                del self.cart[pid_str]
                self.save()
                if product:
                    removed.append(product.title)
                else:
                    removed.append(f"Product #{pid}")
        return removed
