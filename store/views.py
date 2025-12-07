from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Product, Category
from django.core.mail import send_mail
from django.conf import settings

# Home view
def home(request):
    featured_products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.all()[:6]
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)

# Product list
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True)
    
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'search_query': search_query,
    }
    return render(request, 'store/product_list.html', context)

# Product detail
def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)

# Dashboard
@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    
    if hasattr(user, 'is_admin') and user.is_admin():
        total_products = Product.objects.count()
        total_categories = Category.objects.count()
        context.update({
            'total_products': total_products,
            'total_categories': total_categories,
        })
        return render(request, 'store/admin_dashboard.html', context)
    elif hasattr(user, 'is_vendor') and user.is_vendor():
        vendor_products = Product.objects.filter(vendor=user)
        context.update({
            'products': vendor_products,
            'total_products': vendor_products.count(),
        })
        return render(request, 'store/vendor_dashboard.html', context)
    else:
        return render(request, 'store/customer_dashboard.html', context)

# Contact page
def contact(request):
    success = False
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')

        if name and email and subject and message:
            try:
                send_mail(
                    subject=f"Contact Form: {subject}",
                    message=f"From: {name} <{email}>\n\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                success = True
            except Exception as e:
                print("Email send failed:", e)
    
    return render(request, 'contact/contact.html', {'success': success})
