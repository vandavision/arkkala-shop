from .test_api import TestProductAPI, TestCommentAPI
from .test_enterprise import TestSeniorGradeQuality
from .test_models import TestShopModels, TestProductFilters
from .test_services import TestProductService, TestInteractionService
from .test_admin import TestShopAdmin
from .test_serializers import TestSerializersCoverage
from .test_repositories import TestProductRepository

__all__: list[str] = [
    "TestProductAPI",
    "TestCommentAPI",
    "TestSeniorGradeQuality",
    "TestShopModels",
    "TestProductFilters",
    "TestProductService",
    "TestInteractionService",
    "TestShopAdmin",
    "TestSerializersCoverage",
    "TestProductRepository",
]