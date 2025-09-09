from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse


class Category(models.Model):
    """Model for product categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    """Model for products in the store"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    @property
    def discounted_price(self):
        """Calculate the price after discount"""
        if self.discount > 0:
            return self.price * (1 - self.discount / 100)
        return self.price

    @property
    def has_image(self):
        """Return True if the product has an image file path set and file exists on storage."""
        try:
            if self.image and hasattr(self.image, 'storage') and self.image.name:
                return self.image.storage.exists(self.image.name)
        except Exception:
            # If storage check fails, fall back to truthiness of field
            return bool(self.image)
        return False

    @property
    def primary_image_file(self):
        """Return the best available image file object for this product.

        Priority:
        1) Product.image if it exists on storage
        2) ProductImage with is_primary=True if exists and file present
        3) First ProductImage by ordering if file present
        Returns the FileField/File object or None.
        """
        # Direct image on Product
        if self.has_image:
            return self.image

        # Primary gallery image
        try:
            primary = self.images.filter(is_primary=True).first()
            if primary and primary.has_image:
                return primary.image
        except Exception:
            pass

        # First available gallery image
        try:
            first_image = self.images.first()
            if first_image and first_image.has_image:
                return first_image.image
        except Exception:
            pass

        return None

    @property
    def has_primary_image(self):
        return self.primary_image_file is not None

    @property
    def primary_image_url(self):
        file_obj = self.primary_image_file
        if file_obj:
            try:
                return file_obj.url
            except Exception:
                return None
        return None

    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock_quantity > 0

    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not provided
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    """Model for additional product images"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"

    def save(self, *args, **kwargs):
        # If this is set as primary, unset other primary images for this product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

    @property
    def has_image(self):
        """Return True if the image file exists on storage."""
        try:
            if self.image and hasattr(self.image, 'storage') and self.image.name:
                return self.image.storage.exists(self.image.name)
        except Exception:
            return bool(self.image)
        return False

