import pytest
from typing import Any
from unittest.mock import patch
from users.tasks import cleanup_expired_otps
from users.models.otp import OTPRequest

@pytest.mark.django_db
class TestCeleryTasks:
    def test_cleanup_expired_otps_success(self, valid_otp_request: OTPRequest) -> None:
        uuid_str = str(valid_otp_request.uuid)
        result = cleanup_expired_otps(uuid_str)
        
        assert "was successfully deleted" in result
        assert OTPRequest.objects.filter(uuid=uuid_str).exists() is False

    def test_cleanup_expired_otps_not_found(self) -> None:
        result = cleanup_expired_otps("123e4567-e89b-12d3-a456-426614174000")
        assert "not found" in result

    @patch('users.repositories.otp.OTPRepository.get_by_uuid', side_effect=Exception("DB Error"))
    def test_cleanup_expired_otps_exception(self, mock_get: Any) -> None:
        with pytest.raises(Exception):
            cleanup_expired_otps("123e4567-e89b-12d3-a456-426614174000")