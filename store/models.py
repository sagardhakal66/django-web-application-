from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.conf import settings

User = get_user_model()

class Category(models.Model):
    """Product category model"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Product model for e-commerce store"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/')
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'vendor'})

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def is_on_sale(self):
        return self.compare_price and self.compare_price > self.price

    def get_discount_percentage(self):
        if self.is_on_sale():
            discount = ((self.compare_price - self.price) / self.compare_price) * 100
            return round(discount)
        return 0
    
    # ============ UPDATED FOR USD CURRENCY ============
    def get_price_display(self):
        """Return price formatted in US Dollars: $1,350.00"""
        return f"{settings.CURRENCY_SYMBOL}{self.price:,.2f}"
    
    def get_price_no_decimal(self):
        """Return price without decimal: $1,350"""
        return f"{settings.CURRENCY_SYMBOL}{self.price:,.0f}"
    
    def get_compare_price_display(self):
        """Return compare price formatted in US Dollars"""
        if self.compare_price:
            return f"{settings.CURRENCY_SYMBOL}{self.compare_price:,.2f}"
        return ""
    
    def get_compare_price_no_decimal(self):
        """Return compare price without decimal"""
        if self.compare_price:
            return f"{settings.CURRENCY_SYMBOL}{self.compare_price:,.0f}"
        return ""
    
    def get_price_in_lakhs(self):
        """Return price in lakhs format if applicable: Rs. 1.35 Lakh - REMOVED FOR USD"""
        # This method is specific to NPR, removing or modifying
        return f"{settings.CURRENCY_SYMBOL}{self.price:,.2f}"
    
    def get_discount_amount(self):
        """Get discount amount in USD"""
        if self.is_on_sale():
            discount = self.compare_price - self.price
            return f"{settings.CURRENCY_SYMBOL}{discount:,.2f}"
        return ""
    
    def get_formatted_price_data(self):
        """Return all price data in a dictionary"""
        return {
            'price': self.get_price_display(),
            'price_no_decimal': self.get_price_no_decimal(),
            'compare_price': self.get_compare_price_display(),
            'compare_price_no_decimal': self.get_compare_price_no_decimal(),
            'discount_percentage': self.get_discount_percentage(),
            'discount_amount': self.get_discount_amount(),
            'currency_symbol': settings.CURRENCY_SYMBOL,
            'currency_code': settings.CURRENCY_CODE,
        }


class Order(models.Model):
    """Order model to track customer purchases"""
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.TextField()

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = str(uuid.uuid4())[:20]
        super().save(*args, **kwargs)
    
    # ============ UPDATED FOR USD CURRENCY ============
    def get_total_amount_display(self):
        """Return total amount formatted in US Dollars"""
        return f"{settings.CURRENCY_SYMBOL}{self.total_amount:,.2f}"
    
    def get_total_amount_no_decimal(self):
        """Return total amount without decimal"""
        return f"{settings.CURRENCY_SYMBOL}{self.total_amount:,.0f}"
    
    def get_order_summary(self):
        """Return order summary with formatted prices"""
        return {
            'order_number': self.order_number,
            'total_amount': self.get_total_amount_display(),
            'total_amount_no_decimal': self.get_total_amount_no_decimal(),
            'status': self.get_status_display(),
            'items_count': self.items.count(),
            'currency_symbol': settings.CURRENCY_SYMBOL,
            'currency_code': settings.CURRENCY_CODE,
        }


class OrderItem(models.Model):
    """Individual items within an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.price * self.quantity
    
    # ============ UPDATED FOR USD CURRENCY ============
    def get_price_display(self):
        """Return item price formatted in US Dollars"""
        return f"{settings.CURRENCY_SYMBOL}{self.price:,.2f}"
    
    def get_total_price_display(self):
        """Return total price formatted in US Dollars"""
        total = self.get_total_price()
        return f"{settings.CURRENCY_SYMBOL}{total:,.2f}"
    
    def get_item_summary(self):
        """Return item summary with formatted prices"""
        return {
            'product_name': self.product.name,
            'quantity': self.quantity,
            'unit_price': self.get_price_display(),
            'total_price': self.get_total_price_display(),
            'currency_symbol': settings.CURRENCY_SYMBOL,
            'currency_code': settings.CURRENCY_CODE,
        }


class ContactMessage(models.Model):
    """Stores messages sent via the contact form"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"