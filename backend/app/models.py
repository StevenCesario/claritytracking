from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    JSON
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)

# The base class for all our database models.
# It's like the foundation of our building; everything else is built on top of it.
class Base(DeclarativeBase):
    pass

# Represents a user account in our system.
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    registered_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    # One-to-one relationship with UserAuth for password storage.
    auth: Mapped["UserAuth"] = relationship(
        back_populates="user",
        uselist=False, # Explicitly define as one-to-one
        cascade="all, delete-orphan" # If a user is deleted, auth record is deleted
    )
    # One user can have many websites they are tracking.
    websites: Mapped[List["Website"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan" # If a user is deleted, their websites are deleted too.
    )

# Securely stores user password hashes, separate from the main user info.
class UserAuth(Base):
    __tablename__ = "user_auth"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    # Relationship back to the User model.
    user: Mapped["User"] = relationship(
        back_populates="auth",
        uselist=False # Explicitly define as one-to-one
    )

# Represents a website that a user is tracking with ClarityPixel.
class Website(Base):
    __tablename__ = "websites"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    url: Mapped[str] = mapped_column(String(2048)) # The URL of the website.
    name: Mapped[str] = mapped_column(String(100)) # A friendly name for the site.
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    # One website can be connected to multiple tracking platforms (Meta, TikTok, etc.).
    connections: Mapped[List["Connection"]] = relationship(
        back_populates="website",
        cascade="all, delete-orphan" # If a website is deleted, its connections go too.
    )
    user: Mapped["User"] = relationship(back_populates="websites")

# Represents a connection to a specific ad platform (like Meta, TikTok, or Shopify).
# This is the key to our "platform agnostic" future.
PLATFORMS = ("meta", "shopify", "tiktok")
class Connection(Base):
    __tablename__ = "connections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    website_id: Mapped[int] = mapped_column(ForeignKey("websites.id"))
    platform: Mapped[str] = mapped_column(String(50)) # e.g., "meta", "shopify", "tiktok"
    
    # Stores platform-specific IDs, like Pixel ID for Meta or Store ID for Shopify.
    # Using JSON allows us to be flexible for future platforms.
    platform_identifiers: Mapped[dict] = mapped_column(JSON) 
    
    # Securely stores encrypted access tokens for making API calls.
    encrypted_access_token: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    website: Mapped["Website"] = relationship(back_populates="connections")
