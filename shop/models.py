"""Shop-models module."""
from django.db import models
from io import BytesIO
from PIL import Image
from django.core.files import File
from django.utils.text import slugify
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.models import CloudinaryField
from django.db.models.signals import pre_delete
from django.dispatch import receiver


# Create your models here.


class Product(models.Model):
    CATEGORY_CHOICES = (
        ("DECK", "DECK"),)
    # ("FEBRUARY", "February"),,)

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField()
    slug = models.SlugField(blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=5)
    image = CloudinaryField('image')
    on_sale = models.BooleanField(default=False)
    sale_percentage = models.IntegerField(
        'Discount percentage', blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        url = f'/{self.category}/{self.slug}/'
        return url


@receiver(pre_delete, sender=Product, dispatch_uid='question_delete_signal')
def log_deleted_question(sender, instance, using, **kwargs):
    image = instance.image
    cloudinary.uploader.destroy(image.public_id, invalidate=True)


class ProductImages(models.Model):
    image = CloudinaryField('image', blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def get_image(self):
        if self.image:
            return 'http://127.0.0.1:8000' + self.image.url
        return ''


@receiver(pre_delete, sender=ProductImages, dispatch_uid='question_delete_signal')
def log_deleted_question(sender, instance, using, **kwargs):
    image = instance.image
    cloudinary.uploader.destroy(image.public_id, invalidate=True)


class Order(models.Model):
    CATEGORY_CHOICES = (
        ("processing", "processing"),
        ("shipped", "shipped"),
        ("delivered", "delivered"))
    order_id = models.CharField(max_length=40, unique=True)
    state = models.CharField(max_length=40)
    country = models.CharField(max_length=100)
    zip_code = models.IntegerField()
    adress_line = models.CharField(max_length=225)
    # adress_line =models.CharField(max_length=225)
    paid = models.BooleanField(default=False)
    full_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tracking_number = models.CharField(max_length=200, null=True)
    contact_email = models.EmailField(null=True)
    city = models.CharField(max_length=100, null=True)
    status = models.CharField(choices=CATEGORY_CHOICES,
                              default="processing", max_length=40)


class ItemOrdered(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, to_field='order_id')
