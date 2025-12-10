from django.db import models
from django.contrib.auth import get_user_model
from store.models import Product
from django.conf import settings

User = get_user_model()

class Cart(models.Model):
    """
    Shopping cart model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart ({self.user.username})"
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())
    
    # ============ UPDATED FOR USD CURRENCY ============
    def get_total_price_display(self):
        """Return cart total formatted in US Dollars: $1,350.00"""
        total = self.get_total_price()
        return f"{settings.CURRENCY_SYMBOL}{total:,.2f}"
    
    def get_total_price_no_decimal(self):
        """Return cart total without decimal: $1,350"""
        total = self.get_total_price()
        return f"{settings.CURRENCY_SYMBOL}{total:,.0f}"
    
    def get_cart_summary(self):
        """Return complete cart summary with formatted prices"""
        items = self.items.all()
        item_summaries = []
        
        for item in items:
            item_summaries.append({
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': item.get_price_display(),
                'total_price': item.get_total_price_display(),
            })
        
        return {
            'user': self.user.username,
            'total_items': self.get_total_quantity(),
            'total_amount': self.get_total_price_display(),
            'total_amount_no_decimal': self.get_total_price_no_decimal(),
            'items': item_summaries,
            'currency_symbol': settings.CURRENCY_SYMBOL,
            'currency_code': settings.CURRENCY_CODE,
        }


class CartItem(models.Model):
    """
    Individual items in the shopping cart
    """
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_total_price(self):
        return self.product.price * self.quantity
    
    # ============ UPDATED FOR USD CURRENCY ============
    def get_price_display(self):
        """Return item price formatted in US Dollars"""
        return self.product.get_price_display()
    
    def get_compare_price_display(self):
        """Return compare price if available"""
        if self.product.compare_price:
            return self.product.get_compare_price_display()
        return ""
    
    def get_total_price_display(self):
        """Return total price for this item formatted in US Dollars"""
        total = self.get_total_price()
        return f"{settings.CURRENCY_SYMBOL}{total:,.2f}"
    
    def get_total_price_no_decimal(self):
        """Return total price without decimal"""
        total = self.get_total_price()
        return f"{settings.CURRENCY_SYMBOL}{total:,.0f}"
    
    def get_discount_amount_display(self):
        """Get discount amount for this item if on sale"""
        if self.product.is_on_sale():
            discount_per_item = self.product.compare_price - self.product.price
            total_discount = discount_per_item * self.quantity
            return f"{settings.CURRENCY_SYMBOL}{total_discount:,.0f}"
        return ""
    
    def get_item_summary(self):
        """Return detailed item summary with formatted prices"""
        return {
            'product_id': self.product.id,
            'product_name': self.product.name,
            'product_slug': self.product.slug,
            'quantity': self.quantity,
            'unit_price': self.get_price_display(),
            'unit_compare_price': self.get_compare_price_display(),
            'total_price': self.get_total_price_display(),
            'discount_amount': self.get_discount_amount_display(),
            'is_on_sale': self.product.is_on_sale(),
            'discount_percentage': self.product.get_discount_percentage(),
            'image_url': self.product.image.url if self.product.image else '',
            'stock': self.product.stock,
            'currency_symbol': settings.CURRENCY_SYMBOL,
            'currency_code': settings.CURRENCY_CODE,
        }
    
    class Meta:
        unique_together = ['cart', 'product']