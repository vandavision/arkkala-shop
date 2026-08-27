import uuid
import requests
from typing import Any
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from faker import Faker

from home.models import (
    Story, Slider, Banner, StoreReview, SiteSetting, FAQ, AboutPage
)

class Command(BaseCommand):
    """
    Management command to seed the home app with fake Persian data and media from public APIs.
    """
    help: str = "Seed home app data (Stories, Sliders, Banners, Settings, FAQs, etc.) with fake data and media."

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)
        self.faker: Faker = Faker('fa_IR')
        self.video_url: str = "https://www.w3schools.com/html/mov_bbb.mp4"

    def handle(self, *args: tuple, **options: dict[str, Any]) -> None:
        self.stdout.write(self.style.WARNING("Starting to seed Home app... This might take a while due to downloads."))

        self._seed_site_setting()
        self._seed_about_page()
        self._seed_faqs(count=5)
        self._seed_reviews(count=10)
        self._seed_sliders(count=3)
        self._seed_banners(count=4)
        self._seed_stories(count=5)

        self.stdout.write(self.style.SUCCESS("Home App successfully seeded with fake data and media!"))

    def _get_random_image_url(self, width: int = 800, height: int = 600) -> str:
        """
        Generate a random image URL from Picsum to avoid caching issues.
        """
        random_id: str = uuid.uuid4().hex[:6]
        return f"https://picsum.photos/seed/{random_id}/{width}/{height}"

    def _download_file(self, url: str, prefix: str, ext: str) -> ContentFile | None:
        """
        Download a file from a URL and return a Django ContentFile.
        """
        try:
            response: requests.Response = requests.get(url, timeout=15)
            response.raise_for_status()
            file_name: str = f"{prefix}_{uuid.uuid4().hex[:8]}.{ext}"
            return ContentFile(response.content, name=file_name)
        except requests.RequestException:
            self.stderr.write(self.style.ERROR(f"Failed to download media from {url}"))
            return None

    def _seed_site_setting(self) -> None:
        """
        Create or update the singleton SiteSetting with fake data and a logo.
        """
        setting, created = SiteSetting.objects.get_or_create(pk=1)
        setting.site_name = self.faker.company()
        setting.about_us_footer = self.faker.text(max_nb_chars=200)
        setting.phone_number = self.faker.phone_number()
        setting.seller_legal_name = self.faker.name()
        setting.seller_address = self.faker.address()
        setting.seller_economic_code = str(self.faker.random_number(digits=12))
        setting.seller_postal_code = self.faker.postcode()
        setting.telegram = "https://t.me/fake_arkkala"
        setting.instagram = "https://instagram.com/fake_arkkala"

        logo_file = self._download_file(self._get_random_image_url(200, 200), "logo", "jpg")
        if logo_file:
            setting.logo.save(logo_file.name, logo_file, save=False)

        setting.save()
        self.stdout.write(self.style.SUCCESS("SiteSetting seeded."))

    def _seed_about_page(self) -> None:
        """
        Create or update the AboutPage.
        """
        about_page, created = AboutPage.objects.get_or_create(title="درباره ما")
        about_page.content = "\n\n".join(self.faker.paragraphs(nb=5))
        
        image_file = self._download_file(self._get_random_image_url(1200, 800), "about", "jpg")
        if image_file:
            about_page.image.save(image_file.name, image_file, save=False)
            
        about_page.save()
        self.stdout.write(self.style.SUCCESS("AboutPage seeded."))

    def _seed_faqs(self, count: int) -> None:
        """
        Generate fake FAQs.
        """
        FAQ.objects.all().delete()
        faqs: list[FAQ] = []
        for i in range(count):
            faqs.append(
                FAQ(
                    question=self.faker.sentence(),
                    answer=self.faker.paragraph(),
                    order=i,
                    is_active=True
                )
            )
        FAQ.objects.bulk_create(faqs)
        self.stdout.write(self.style.SUCCESS(f"{count} FAQs seeded."))

    def _seed_reviews(self, count: int) -> None:
        """
        Generate fake Store Reviews.
        """
        StoreReview.objects.all().delete()
        reviews: list[StoreReview] = []
        for _ in range(count):
            reviews.append(
                StoreReview(
                    user_name=self.faker.name(),
                    body=self.faker.text(max_nb_chars=150),
                    is_active=True
                )
            )
        StoreReview.objects.bulk_create(reviews)
        self.stdout.write(self.style.SUCCESS(f"{count} StoreReviews seeded."))

    def _seed_sliders(self, count: int) -> None:
        """
        Generate fake Sliders with downloaded images.
        """
        Slider.objects.all().delete()
        for i in range(count):
            slider = Slider(
                title=self.faker.catch_phrase(),
                link=self.faker.url(),
                order=i,
                is_active=True
            )
            img_file = self._download_file(self._get_random_image_url(1920, 600), "slider", "jpg")
            if img_file:
                slider.image.save(img_file.name, img_file, save=False)
            slider.save()
        self.stdout.write(self.style.SUCCESS(f"{count} Sliders seeded."))

    def _seed_banners(self, count: int) -> None:
        """
        Generate fake Banners with downloaded images.
        """
        Banner.objects.all().delete()
        positions: list[str] = ['top_left', 'top_right', 'middle_row', 'bottom_row']
        for i in range(count):
            banner = Banner(
                title=self.faker.catch_phrase(),
                link=self.faker.url(),
                position=positions[i % len(positions)],
                is_active=True
            )
            img_file = self._download_file(self._get_random_image_url(800, 400), "banner", "jpg")
            if img_file:
                banner.image.save(img_file.name, img_file, save=False)
            banner.save()
        self.stdout.write(self.style.SUCCESS(f"{count} Banners seeded."))

    def _seed_stories(self, count: int) -> None:
        """
        Generate fake Stories with downloaded images and occasional videos.
        """
        Story.objects.all().delete()
        for i in range(count):
            story = Story(
                title=self.faker.word(),
                link=self.faker.url(),
                is_active=True
            )
            img_file = self._download_file(self._get_random_image_url(1080, 1920), "story_cover", "jpg")
            if img_file:
                story.image.save(img_file.name, img_file, save=False)
            
            if i % 2 == 0:
                vid_file = self._download_file(self.video_url, "story_video", "mp4")
                if vid_file:
                    story.video.save(vid_file.name, vid_file, save=False)
                    
            story.save()
        self.stdout.write(self.style.SUCCESS(f"{count} Stories seeded."))