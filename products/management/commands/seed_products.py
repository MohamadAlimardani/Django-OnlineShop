import os
import random
import urllib.error
import urllib.request
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from products.models import Category, Product


IMAGE_URLS = [
    "https://images.pexels.com/photos/1191318/pexels-photo-1191318.jpeg",
    "https://images.pexels.com/photos/1058771/pexels-photo-1058771.jpeg",
    "https://images.pexels.com/photos/1323020/pexels-photo-1323020.jpeg",
    "https://images.pexels.com/photos/4065159/pexels-photo-4065159.jpeg",
    "https://images.pexels.com/photos/1824189/pexels-photo-1824189.jpeg",
    "https://images.pexels.com/photos/4505452/pexels-photo-4505452.jpeg",
    "https://images.pexels.com/photos/4273440/pexels-photo-4273440.jpeg",
    "https://images.pexels.com/photos/2108514/pexels-photo-2108514.jpeg",
    "https://images.pexels.com/photos/7184409/pexels-photo-7184409.jpeg",
    "https://images.pexels.com/photos/10295068/pexels-photo-10295068.jpeg",
    "https://images.pexels.com/photos/35267737/pexels-photo-35267737.jpeg",
    "https://images.pexels.com/photos/4505447/pexels-photo-4505447.jpeg",
    "https://images.pexels.com/photos/6640243/pexels-photo-6640243.jpeg"
]

CATEGORIES = [
    "Ceramic",
    "Terracotta",
    "Concrete",
    "Metal",
    "Hanging",
    "Self-Watering",
    "Indoor Pots",
    "Outdoor Pots",
    "Planter Sets",
    "Rattan",
]

ADJECTIVES = [
    "Minimal",
    "Matte",
    "Glazed",
    "Rustic",
    "Modern",
    "Classic",
    "Stacked",
    "Ridged",
    "Sleek",
    "Textured",
    "Handcrafted",
    "Natural",
    "Soft-Tone",
    "Tall",
    "Wide",
    "Compact",
    "Studio",
    "Pebble",
    "Stone",
    "Sand",
]

POT_TYPES = [
    "Cylinder Planter",
    "Bowl Planter",
    "Footed Pot",
    "Hanging Planter",
    "Window Box",
    "Herb Pot",
    "Nursery Pot",
    "Desk Pot",
    "Corner Planter",
    "Oval Planter",
    "Cube Planter",
    "Urn Planter",
    "Tapered Pot",
    "Ribbed Planter",
    "Self-Watering Pot",
    "Pedestal Planter",
    "Round Pot",
    "Square Pot",
    "Rattan Basket Pot",
    "Terrace Planter",
]

DESC_LEADS = [
    "Designed for everyday greenery,",
    "Built for indoor and patio styling,",
    "Crafted to highlight your favorite plants,",
    "Made with a clean, modern profile,",
    "Shaped for balanced proportions,",
    "Finished with a soft matte glaze,",
    "Inspired by natural clay textures,",
    "Engineered for easy plant care,",
]

DESC_MIDDLES = [
    "this pot features a smooth finish and subtle rim.",
    "it includes a drainage hole and matching saucer.",
    "its lightweight build makes rearranging simple.",
    "the tapered silhouette fits shelves and sills.",
    "its textured surface adds depth without noise.",
    "the wide mouth supports fuller root growth.",
    "its neutral tone blends across rooms and patios.",
    "the elevated base improves airflow and drainage.",
]

DESC_ENDS = [
    "Ideal for succulents, herbs, and houseplants.",
    "A versatile pick for modern plant displays.",
    "Pairs well with warm woods and soft linens.",
    "Looks great in clusters or as a statement piece.",
    "Finished to resist fading and daily wear.",
    "A reliable staple for your plant corner.",
]

SIZES = ["Small", "Medium", "Large", "XL"]


def _download_bytes(url, cache):
    if url in cache:
        return cache[url]
    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            data = response.read()
        if data:
            cache[url] = data
            return data
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return None
    return None


def _make_svg_placeholder(name, seed):
    colors = ["#606c38", "#283618", "#d18441", "#e2b35b", "#fefae0"]
    rng = random.Random(seed)
    c1 = rng.choice(colors)
    c2 = rng.choice(colors)
    title = name[:28]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="600">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#bg)"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
        font-family="Georgia, serif" font-size="42" fill="#fefae0"
        letter-spacing="1">{title}</text>
</svg>"""
    return svg.encode("utf-8")


class Command(BaseCommand):
    help = "Seed the database with realistic flower pot products."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=50)
        parser.add_argument("--seed", type=int, default=11)
        parser.add_argument("--clear", action="store_true")

    def handle(self, *args, **options):
        count = options["count"]
        seed = options["seed"]
        clear = options["clear"]

        if clear:
            Product.objects.all().delete()

        category_map = {}
        for name in CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={"slug": slugify(name)}
            )
            category_map[name] = cat
        
        rng = random.Random(seed)
        image_cache = {}

        created = 0
        for i in range(count):
            adjective = rng.choice(ADJECTIVES)
            pot_type = rng.choice(POT_TYPES)
            size = rng.choice(SIZES)
            name = f"{adjective} {pot_type} ({size})"

            description = (
                f"{rng.choice(DESC_LEADS)} {rng.choice(DESC_MIDDLES)} "
                f"{rng.choice(DESC_ENDS)}"
            )

            category_name = rng.choice(CATEGORIES)
            category_obj = category_map[category_name]
            
            dollars = rng.randint(8, 120)
            cents = rng.choice([0, 5, 9, 25, 49, 75, 95])
            price = Decimal(f"{dollars}.{cents:02d}")
            stock = rng.randint(5, 120)

            product = Product(
                name=name,
                description=description,
                category=category_obj,
                price=price,
                stock=stock,
            )

            image_url = rng.choice(IMAGE_URLS)
            image_bytes = _download_bytes(image_url, image_cache)

            if not image_bytes:
                image_bytes = _make_svg_placeholder(name, seed + i)
                ext = ".svg"
            else:
                ext = os.path.splitext(image_url.split("?")[0])[1] or ".jpg"

            base_name = f"{slugify(name)}-{i}"
            filename = f"{base_name}{ext}"
            product.image.save(filename, ContentFile(image_bytes), save=False)

            product.save()
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} products."))
