from django.db import transaction
from shop.models.product import Product
from shop.domain.exceptions import InvalidProductDataError
from shop.application.dto.commands import CreateProductCommandDTO
from shop.application.ports.repositories import ProductRepositoryPort
from shop.application.ports.event_bus import EventBusPort

class CreateProductCommand:
    """Isolates Product persistence enforcing strict wholesale rules outside Model."""
    
    def __init__(self, product_repo: ProductRepositoryPort, event_bus: EventBusPort) -> None:
        self.product_repo = product_repo
        self.event_bus = event_bus

    @transaction.atomic
    def execute(self, dto: CreateProductCommandDTO) -> Product:
        """Validates advanced business logic before triggering ORM commits."""
        if dto.is_wholesale:
            if not dto.wholesale_min_quantity or dto.wholesale_min_quantity < 2:
                raise InvalidProductDataError("برای فروش عمده، حداقل تعداد باید بیشتر از ۱ باشد.")
            if dto.wholesale_base_price is None:
                raise InvalidProductDataError("برای فروش عمده، تعیین قیمت پایه عمده الزامی است.")
            if dto.wholesale_base_price >= dto.base_price:
                raise InvalidProductDataError("قیمت عمده باید کمتر از قیمت پایه باشد.")

        product = Product(
            title=dto.title,
            slug=dto.slug,
            description=dto.description,
            base_price=dto.base_price,
            category_id=dto.category_id,
            brand_id=dto.brand_id,
            is_wholesale=dto.is_wholesale,
            wholesale_min_quantity=dto.wholesale_min_quantity,
            wholesale_base_price=dto.wholesale_base_price,
        )
        
        return self.product_repo.save_product(product)