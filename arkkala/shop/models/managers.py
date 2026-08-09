from django.db import models
from shop.models.querysets import ProductQuerySet

ProductManager = models.Manager.from_queryset(ProductQuerySet)