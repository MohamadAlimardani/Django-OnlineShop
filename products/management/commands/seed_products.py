import random
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from products.models import Category, Product


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
    "Minimal", "Matte", "Glazed", "Rustic", "Modern", "Classic", "Stacked", "Ridged",
    "Sleek", "Textured", "Handcrafted", "Natural", "Soft-Tone", "Tall", "Wide",
    "Compact", "Studio", "Pebble", "Stone", "Sand",
]

POT_TYPES = [
    "Cylinder Planter", "Bowl Planter", "Footed Pot", "Hanging Planter", "Window Box",
    "Herb Pot", "Nursery Pot", "Desk Pot", "Corner Planter", "Oval Planter",
    "Cube Planter", "Urn Planter", "Tapered Pot", "Ribbed Planter",
    "Self-Watering Pot", "Pedestal Planter", "Round Pot", "Square Pot",
    "Rattan Basket Pot", "Terrace Planter",
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

ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def _make_svg_placeholder(name: str, seed: int) -> bytes:
    colors = ["#606c38", "#283618", "#d18441", "#e2b35b", "#fefae0"]
    rng = random.Random(seed)
    c1 = rng.choice(colors)
    c2 = rng.choice(colors)
    title = name[:28].replace("&", "and")
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


def _unique_slug(base: str, used_slugs: set[str], max_len: int = 255) -> str:
    base = (base or "product")[:max_len]
    slug = base
    counter = 1
    while slug in used_slugs:
        suffix = f"-{counter}"
        slug = f"{base[: max_len - len(suffix)]}{suffix}"
        counter += 1
    used_slugs.add(slug)
    return slug


def _collect_images(images_dir: Path) -> list[Path]:
    if not images_dir.exists() or not images_dir.is_dir():
        return []
    files = []
    for p in images_dir.iterdir():
        if p.is_file() and p.suffix.lower() in ALLOWED_IMAGE_EXTS:
            files.append(p)
    return files


class Command(BaseCommand):
    help = "Seed the database with realistic flower pot products using local images."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=50)
        parser.add_argument("--seed", type=int, default=11)
        parser.add_argument("--clear", action="store_true")
        parser.add_argument("--progress-every", type=int, default=10)

        # You can pass an absolute path or a path relative to BASE_DIR
        parser.add_argument(
            "--images-dir",
            type=str,
            default="products/seed_images",
            help="Folder containing images (relative to BASE_DIR or absolute).",
        )

    def handle(self, *args, **options):
        count: int = options["count"]
        seed: int = options["seed"]
        clear: bool = options["clear"]
        progress_every: int = options["progress_every"]
        images_dir_arg: str = options["images_dir"]

        if clear:
            Product.objects.all().delete()

        # Categories once
        category_map: dict[str, Category] = {}
        for name in CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={"slug": slugify(name)[:255] or name.lower()},
            )
            category_map[name] = cat

        rng = random.Random(seed)

        # Preload slugs once
        used_slugs = set(Product.objects.values_list("slug", flat=True))

        # Resolve images dir (relative -> BASE_DIR)
        images_dir_path = Path(images_dir_arg)
        if not images_dir_path.is_absolute():
            images_dir_path = Path(settings.BASE_DIR) / images_dir_path

        image_files = _collect_images(images_dir_path)
        if image_files:
            self.stdout.write(self.style.SUCCESS(
                f"Found {len(image_files)} images in: {images_dir_path}"
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f"No images found in: {images_dir_path} (will use SVG placeholders)"
            ))

        created = 0
        for i in range(count):
            if progress_every and (i % progress_every == 0):
                self.stdout.write(f"Seeding {i}/{count}...")

            adjective = rng.choice(ADJECTIVES)
            pot_type = rng.choice(POT_TYPES)
            size = rng.choice(SIZES)
            name = f"{adjective} {pot_type} ({size})"

            description = (
                f"{rng.choice(DESC_LEADS)} {rng.choice(DESC_MIDDLES)} "
                f"{rng.choice(DESC_ENDS)}"
            )

            category_obj = category_map[rng.choice(CATEGORIES)]
            dollars = rng.randint(8, 120)
            cents = rng.choice([0, 5, 9, 25, 49, 75, 95])
            price = Decimal(f"{dollars}.{cents:02d}")
            stock = rng.randint(5, 120)

            base_slug = slugify(name) or f"product-{i}"
            slug = _unique_slug(base_slug, used_slugs)

            product = Product(
                name=name,
                description=description,
                category=category_obj,
                price=price,
                stock=stock,
                slug=slug,
            )

            # Pick a random local image (offline + fast)
            if image_files:
                chosen = rng.choice(image_files)
                try:
                    image_bytes = chosen.read_bytes()
                    ext = chosen.suffix.lower() or ".jpg"
                except OSError:
                    image_bytes = _make_svg_placeholder(name, seed + i)
                    ext = ".svg"
            else:
                image_bytes = _make_svg_placeholder(name, seed + i)
                ext = ".svg"

            filename = f"{slug}-{i}{ext}"
            product.image.save(filename, ContentFile(image_bytes), save=False)

            product.save()
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} products."))
