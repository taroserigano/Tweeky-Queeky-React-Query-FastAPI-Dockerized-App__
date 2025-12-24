from beanie import Document
from pydantic import Field, EmailStr, ConfigDict
import bcrypt
from datetime import datetime
from typing import Optional


class User(Document):
    name: str
    email: EmailStr = Field(unique=True, index=True)
    password: str
    is_admin: bool = Field(default=False, alias="isAdmin")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password123",
                "isAdmin": False
            }
        }
    )

    class Settings:
        name = "users"
        use_state_management = True

    def verify_password(self, plain_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), self.password.encode('utf-8'))

    def hash_password(self):
        """Hash the password before saving"""
        self.password = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    async def save(self, *args, **kwargs):
        """Override save to hash password if modified"""
        # Check if this is a new document or password was modified
        if self.id is None or self.is_changed:
            # Only hash if password appears to be plain text (not already hashed)
            if not self.password.startswith("$2b$"):
                self.hash_password()
        self.updated_at = datetime.utcnow()
        return await super().save(*args, **kwargs)
