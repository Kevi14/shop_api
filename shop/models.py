"""Shop-models module."""
from django.db import models
from io import BytesIO
from PIL import Image
from django.core.files import File
from django.utils.text import slugify
import cloudinary
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
    image = cloudinary.models.CloudinaryField('image')
    thumbnail = cloudinary.models.CloudinaryField('image')
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

    def get_image(self):
        if self.image:
            return 'http://127.0.0.1:8000' + self.image.url
        return ''

    def get_absolute_url(self):
        url = f'/{self.category}/{self.slug}/'
        return url

    def get_thumbnail(self):
        if self.thumbnail:
            return 'http://127.0.0.1:8000' + self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()

                return 'http://127.0.0.1:8000' + self.thumbnail.url
            else:
                return ''

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail


class ProductImages(models.Model):
    image = models.ImageField(upload_to='', blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def get_image(self):
        if self.image:
            return 'http://127.0.0.1:8000' + self.image.url
        return ''


class Order(models.Model):
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
    city = models.CharField(max_length=100,null=True)
    # status = models.CharField(choices=)


class ItemOrdered(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, to_field='order_id')
