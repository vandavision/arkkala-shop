import pytest
from shop.models import Product, Comment
from shop.application.dto.commands import CreateCommentCommandDTO
from shop.application.commands.increment_view_count import IncrementViewCountCommand
from shop.application.commands.create_comment import CreateCommentCommand
import shop.dependencies as deps

@pytest.mark.django_db
class TestApplicationCommands:
    """Validates Command and Query executions utilizing isolated DI scopes."""

    def test_atomic_view_count_increment(self, product: Product) -> None:
        initial_views: int = product.view_count
        cmd: IncrementViewCountCommand = deps.get_increment_view_count_command()
        cmd.execute(product.slug)
        product.refresh_from_db()
        assert product.view_count == initial_views + 1

    def test_create_comment_command(self, product: Product) -> None:
        dto = CreateCommentCommandDTO(
            product_slug=product.slug,
            body="Isolating use cases rocks",
            rating=5,
            user_id=None
        )
        cmd: CreateCommentCommand = deps.get_create_comment_command()
        result = cmd.execute(dto)
        assert result.body == "Isolating use cases rocks"
        assert Comment.objects.count() == 1