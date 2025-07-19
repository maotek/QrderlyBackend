import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models


class Restaurant(models.Model):
    name        = models.CharField(max_length=200)
    code        = models.CharField(
                    max_length=12,
                    unique=True,
                    editable=True,
                    blank=True,
                    help_text="URL-safe identifier, e.g. QR token"
                )
    address     = models.CharField(max_length=300, blank=True)
    phone       = models.CharField(max_length=20, blank=True)
    logo        = models.ImageField(
                    upload_to="restaurant_logos/",
                    blank=True,
                    null=True,
                    default="restaurant_logos/DEFAULTLOGO.png",
                    help_text="Upload a square PNG or JPG logo"
                  )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # first delete the file
        if self.logo:
            self.logo.delete(save=False)
        # then delete the model
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.code:
            # generate something like “AbC12XyZ34Q”
            self.code = secrets.token_urlsafe(8)
        super().save(*args, **kwargs)


class Table(models.Model):
    restaurant   = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="tables"
    )
    table_number = models.PositiveIntegerField(
        help_text="The human‑visible table number (e.g. 1, 2, 3…)",
    )
    code = models.CharField(
        max_length=32,
        unique=True,
        editable=True,
        blank=True,
        help_text="Opaque token used in the URL"
    )
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering        = ["restaurant", "table_number"]

    def save(self, *args, **kwargs):
        if not self.code:
            # generate a URL‑safe random token
            self.code = secrets.token_urlsafe(24)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.restaurant.name} – Table {self.table_number}"


class StaffUser(AbstractUser):
    """
    A restaurant staff account, tied to one Restaurant.
    Inherits:
     - username (unique)
     - password (hashed)
     - first_name, last_name, email, is_staff, is_superuser, is_active, etc.
    """
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        null=True,  # ← allow NULL in the database
        blank=True,  # ← allow blank in forms/admin
        related_name="staff_users",
        help_text="Which restaurant this user works at",
    )
    is_admin = models.BooleanField(
        default=False,
        help_text="Owner or manager if True; regular staff if False"
    )

    def __str__(self):
        if self.restaurant:
            return f"{self.username} @ {self.restaurant.name}"
        return self.username


class DishCategory(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="dish_categories",
    )
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "DishCategory"
        verbose_name_plural = "DishCategories"
        unique_together = ("restaurant", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.restaurant.name} – {self.name}"


class Tag(models.Model):
    """
    Simple tag that can be reused across dishes,
    even in different restaurants if you like.
    """
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name


class Dish(models.Model):
    category = models.ForeignKey(
        DishCategory,
        on_delete=models.CASCADE,
        related_name="dishes",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(
        upload_to="dish_images/",
        blank=True,
        null=True,
        default="dish_images/DEFAULTDISH.jpg",
        help_text="Optional picture of the dish",
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="dishes",
        help_text="Select zero or more tags",
    )

    class Meta:
        verbose_name = "Dish"
        verbose_name_plural = "Dishes"
        unique_together = ("category", "name")
        ordering = ["category__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.category.name})"