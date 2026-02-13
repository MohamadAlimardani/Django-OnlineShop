from decimal import Decimal
from products.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        
        if not cart:
            cart = self.session['cart'] = {}
        
        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.id)
        
        if product.stock < quantity:
            return
        
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        
        new_quantity = self.cart[product_id]['quantity'] + quantity
        
        if new_quantity <= 0:
            del self.cart[product_id]
        
        elif new_quantity <= product.stock:
            self.cart[product_id]['quantity'] = new_quantity
        print(f"\n\n\n\nThis is Cart:\n{self.cart}\n\n\n\n")
        self.save()
    
    def update(self, product, quantity):
        product_id = str(product.id)
        
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]['quantity'] = quantity
            else:
                del self.cart[product_id]
            
            print(f"\n\n\n\nThis is Cart:\n{self.cart}\n\n\n\n")
            self.save()
    
    def save(self):
        self.session.modified = True
    
    def remove(self, product):
        product_id = str(product.id)
        
        if product_id in self.cart:
            del self.cart[product_id]
            print(f"\n\n\n\nThis is Cart:\n{self.cart}\n\n\n\n")
            self.save()
    
    def __len__(self):
        return len(self.cart)
    
    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        
        for product in products:
            self.cart[str(product.id)]['product'] = product
        
        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = Decimal(item['price'] * item['quantity'])
            print(f"\n\n\n{item}\n\n\n")
            yield item
    
    def get_quantity(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            return self.cart[product_id]['quantity']
        return 0
    
    def get_total_price(self):
        return sum(
            Decimal(item['price'] * item['quantity'])
            for item in self.cart.values()
        )
    
    def get_total_items_in_cart(self):
        return len(self.cart.keys())

    def clear(self):
        self.session.pop('cart', None)
        self.save()
