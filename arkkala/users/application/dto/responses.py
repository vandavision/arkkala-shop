from dataclasses import dataclass

@dataclass(frozen=True)
class TokenResponseDTO:
    """
    Carries strictly generated token pairs avoiding external dependency coupling.
    """
    access_token: str
    refresh_token: str
    is_new_user: bool = False