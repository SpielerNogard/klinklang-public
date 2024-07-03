from .models import EmailCodeItem
from typing import Optional


class Database:
    def save_code_for_email(self, item: EmailCodeItem):
        pass

    def get_code_for_email(self, email: str) -> Optional[EmailCodeItem]:
        pass
