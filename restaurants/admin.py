import secrets
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Restaurant, Table, StaffUser, DishCategory, Dish, Tag


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display    = ["id", "name", "code", "address", "phone", "logo_preview"]
    search_fields   = ["name", "code"]
    readonly_fields = ["logo_preview"]
    fieldsets = (
        (None, {"fields": ("name", "code", "address", "phone")}),
        ("Logo", {"fields": ("logo", "logo_preview")}),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="height:60px;object-fit:contain;"/>',
                obj.logo.url
            )
        return "(No logo)"
    logo_preview.short_description = "Logo Preview"



@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display    = ["id", "restaurant", "table_number", "code"]
    list_filter     = ["restaurant"]
    search_fields   = ["code", "restaurant__name"]
    fieldsets = (
        (None, {"fields": ("restaurant", "table_number", "code")}),
    )


@admin.register(StaffUser)
class StaffUserAdmin(UserAdmin):
    model = StaffUser
    list_display = ["username", "first_name", "last_name", "restaurant", "is_admin", "is_active", "is_superuser"]
    list_filter  = ["restaurant", "is_admin", "is_active"]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Permissions", {
            "fields": ("is_admin", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        ("Restaurant", {"fields": ("restaurant",)}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )


@admin.register(DishCategory)
class DishCategoriesAdmin(admin.ModelAdmin):
    list_display = ["restaurant", "name"]
    search_fields = ["restaurant_name", "name"]


@admin.register(Dish)
class DishesAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price"]
    list_filter = ["category", "tags"]
    search_fields = ["name", "description"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]