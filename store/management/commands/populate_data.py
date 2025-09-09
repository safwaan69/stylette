from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product, ProductImage
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories_data = [
            {'name': 'T-Shirts', 'slug': 't-shirts', 'description': 'Comfortable and stylish t-shirts for every occasion'},
            {'name': 'Jeans', 'slug': 'jeans', 'description': 'Classic and modern jeans in various fits and washes'},
            {'name': 'Dresses', 'slug': 'dresses', 'description': 'Elegant dresses for casual and formal occasions'},
            {'name': 'Shoes', 'slug': 'shoes', 'description': 'Footwear for every style and season'},
            {'name': 'Accessories', 'slug': 'accessories', 'description': 'Complete your look with our accessories'},
            {'name': 'Jackets', 'slug': 'jackets', 'description': 'Stay warm and stylish with our jacket collection'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create products
        products_data = [
            # T-Shirts
            {'name': 'Classic White T-Shirt', 'category': 'T-Shirts', 'price': 19.99, 'discount': 10, 'stock': 50, 'description': 'A timeless white t-shirt made from premium cotton. Perfect for layering or wearing on its own.'},
            {'name': 'Graphic Print T-Shirt', 'category': 'T-Shirts', 'price': 24.99, 'discount': 0, 'stock': 30, 'description': 'Express your style with this trendy graphic print t-shirt. Soft and comfortable fit.'},
            {'name': 'V-Neck T-Shirt', 'category': 'T-Shirts', 'price': 22.99, 'discount': 15, 'stock': 25, 'description': 'Elegant v-neck design in various colors. Great for both casual and semi-formal occasions.'},
            
            # Jeans
            {'name': 'Classic Blue Jeans', 'category': 'Jeans', 'price': 59.99, 'discount': 20, 'stock': 40, 'description': 'Traditional blue jeans with a comfortable fit. Made from durable denim material.'},
            {'name': 'Skinny Fit Jeans', 'category': 'Jeans', 'price': 69.99, 'discount': 0, 'stock': 35, 'description': 'Modern skinny fit jeans that hug your curves. Available in multiple washes.'},
            {'name': 'High-Waisted Jeans', 'category': 'Jeans', 'price': 64.99, 'discount': 12, 'stock': 28, 'description': 'Flattering high-waisted design with a vintage-inspired look. Comfortable and stylish.'},
            
            # Dresses
            {'name': 'Summer Floral Dress', 'category': 'Dresses', 'price': 79.99, 'discount': 25, 'stock': 20, 'description': 'Light and airy floral dress perfect for summer days. Flowing silhouette with beautiful patterns.'},
            {'name': 'Little Black Dress', 'category': 'Dresses', 'price': 89.99, 'discount': 0, 'stock': 15, 'description': 'The essential little black dress. Versatile and elegant for any occasion.'},
            {'name': 'Maxi Evening Dress', 'category': 'Dresses', 'price': 129.99, 'discount': 30, 'stock': 12, 'description': 'Stunning maxi dress for special occasions. Elegant design with attention to detail.'},
            
            # Shoes
            {'name': 'Classic Sneakers', 'category': 'Shoes', 'price': 89.99, 'discount': 15, 'stock': 45, 'description': 'Comfortable and stylish sneakers for everyday wear. Available in multiple colors.'},
            {'name': 'Leather Boots', 'category': 'Shoes', 'price': 149.99, 'discount': 0, 'stock': 25, 'description': 'Premium leather boots with excellent craftsmanship. Perfect for fall and winter.'},
            {'name': 'High Heels', 'category': 'Shoes', 'price': 99.99, 'discount': 20, 'stock': 30, 'description': 'Elegant high heels for formal occasions. Comfortable design with stylish appeal.'},
            
            # Accessories
            {'name': 'Leather Handbag', 'category': 'Accessories', 'price': 79.99, 'discount': 10, 'stock': 20, 'description': 'Premium leather handbag with multiple compartments. Perfect for daily use.'},
            {'name': 'Silk Scarf', 'category': 'Accessories', 'price': 39.99, 'discount': 0, 'stock': 35, 'description': 'Luxurious silk scarf with beautiful patterns. Adds elegance to any outfit.'},
            {'name': 'Statement Necklace', 'category': 'Accessories', 'price': 49.99, 'discount': 18, 'stock': 25, 'description': 'Bold statement necklace to complete your look. Eye-catching design with quality materials.'},
            
            # Jackets
            {'name': 'Denim Jacket', 'category': 'Jackets', 'price': 69.99, 'discount': 22, 'stock': 30, 'description': 'Classic denim jacket with a modern fit. Versatile piece for layering.'},
            {'name': 'Leather Jacket', 'category': 'Jackets', 'price': 199.99, 'discount': 0, 'stock': 15, 'description': 'Premium leather jacket with edgy style. A timeless piece for your wardrobe.'},
            {'name': 'Blazer', 'category': 'Jackets', 'price': 119.99, 'discount': 25, 'stock': 18, 'description': 'Professional blazer perfect for work or formal events. Tailored fit with quality fabric.'},
        ]
        
        for product_data in products_data:
            category = next(cat for cat in categories if cat.name == product_data['category'])
            
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'category': category,
                    'price': Decimal(str(product_data['price'])),
                    'discount': product_data['discount'],
                    'stock_quantity': product_data['stock'],
                    'description': product_data['description'],
                    'is_active': True,
                    'is_featured': random.choice([True, False, False, False]),  # 25% chance of being featured
                }
            )
            
            if created:
                self.stdout.write(f'Created product: {product.name}')
        
        # Create a superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@stylette.com',
                password='admin123'
            )
            self.stdout.write('Created superuser: admin (password: admin123)')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )


