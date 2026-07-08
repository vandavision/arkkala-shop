from django import forms
from django.conf import settings
from platform_seo.models import MetaInformation


class MetaInformationForm(forms.ModelForm):
    """
    Form for MetaInformation tailored for Headless (Django + React) Architecture.
    Provides a predefined list of React static pages instead of scraping Django URLs.
    """

    DEFAULT_REACT_PAGES = [
        ('HomePage', 'Home Page (خانه)'),
        ('AboutUsPage', 'About Us Page (درباره ما)'),
        ('FaqPage', 'FAQ Page (سوالات متداول)'),
        ('ContactPage', 'Contact Page (تماس با ما)'),
        ('BlogPage', 'Blog Page (مجله)'),
        ('ShopPage', 'Shop Page (فروشگاه)'),
        ('BrandsPage', 'Brands Page (برندها)'),
        ('CategoriesPage', 'Categories Page (دسته‌بندی‌ها)'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        react_pages = getattr(settings, "REACT_STATIC_PAGES", self.DEFAULT_REACT_PAGES)
        
        self.fields['view_name'] = forms.ChoiceField(
            choices=react_pages,
            label="نام صفحه (React Component)",
            help_text="صفحه‌ای در فرانت‌اند (React) که می‌خواهید این تنظیمات سئو روی آن اعمال شود را انتخاب کنید."
        )

    class Meta:
        model = MetaInformation
        fields = '__all__'