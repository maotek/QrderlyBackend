# restaurants/management/commands/populate_test_data.py

import secrets
from django.core.management.base import BaseCommand
from faker import Faker
from faker_food import FoodProvider

from restaurants.models import Restaurant, Table, StaffUser, DishCategory, Tag, Dish

fake = Faker()
fake.add_provider(FoodProvider)

class Command(BaseCommand):
    help = "Populate the database with test restaurants, tables, staff—and now dishes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--restaurants",
            type=int,
            default=2,
            help="Number of restaurants to create",
        )
        parser.add_argument(
            "--max-tables",
            type=int,
            default=10,
            help="Number of tables per restaurant",
        )
        parser.add_argument(
            "--staff-per-restaurant",
            type=int,
            default=9,
            help="Number of non‑admin staff users per restaurant",
        )
        parser.add_argument(
            "--categories-per-restaurant",
            type=int,
            default=3,
            help="Number of dish categories per restaurant",
        )
        parser.add_argument(
            "--dishes-per-category",
            type=int,
            default=5,
            help="Number of dishes per category",
        )
        parser.add_argument(
            "--tags",
            type=int,
            default=8,
            help="Total number of global tags to create",
        )

    def handle(self, *args, **options):
        n_restaurants  = options["restaurants"]
        max_tables     = options["max_tables"]
        staff_per_rest = options["staff_per_restaurant"]
        cats_per_rest  = options["categories_per_restaurant"]
        dishes_per_cat = options["dishes_per_category"]
        n_tags         = options["tags"]

        # 0) Pre-create some global tags
        global_tags = []
        for _ in range(n_tags):
            name = fake.unique.word().capitalize()
            tag, _ = Tag.objects.get_or_create(name=name)
            global_tags.append(tag)
        self.stdout.write(f"🌍 Created {len(global_tags)} global tags")

        for _ in range(n_restaurants):
            # 1) Create restaurant
            name       = fake.company()
            restaurant = Restaurant.objects.create(
                name=name,
                address=fake.address(),
                phone=fake.phone_number(),
            )
            self.stdout.write(f"\n🏘️  Restaurant {restaurant.code} – {name}")

            # 2) Tables
            for tnum in range(1, max_tables + 1):
                table = Table.objects.create(
                    restaurant=restaurant,
                    table_number=tnum,
                )
            self.stdout.write(f"  • {max_tables} tables created")

            # 3) Staff users
            admin_username = f"{restaurant.code}_admin"
            StaffUser.objects.create_user(
                username=admin_username,
                password="password123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                restaurant=restaurant,
                is_admin=True,
            )
            for _ in range(staff_per_rest):
                StaffUser.objects.create_user(
                    username=fake.unique.user_name(),
                    password="password123",
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    restaurant=restaurant,
                    is_admin=False,
                )
            self.stdout.write(f"  • 1 admin + {staff_per_rest} staff users")

            # 4) Dish categories & dishes
            for _ in range(cats_per_rest):
                cat_name = fake.word().capitalize()
                category = DishCategory.objects.create(
                    restaurant=restaurant,
                    name=cat_name
                )
                dishes = []
                for _ in range(dishes_per_cat):
                    dish = Dish.objects.create(
                        category=category,
                        name=fake.unique.dish().title(),
                        description=fake.sentence(nb_words=12),
                        price=round(fake.pydecimal(left_digits=2, right_digits=2, positive=True), 2),
                    )
                    # assign 0–3 random tags
                    for tag in fake.random_elements(elements=global_tags, length=fake.random_int(0,3), unique=True):
                        dish.tags.add(tag)
                    dishes.append(dish)
                self.stdout.write(f"  • Category “{cat_name}”: {len(dishes)} dishes")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! {n_restaurants} restaurants populated with tables, staff, categories & dishes."
        ))
