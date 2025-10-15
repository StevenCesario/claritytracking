from sqlalchemy.orm import Session

# We import our models (the database blueprint), schemas (the API contract),
# and security functions (the locksmith).
from . import models, schemas, security

# =============================================================================
# USER CRUD OPERATIONS
# =============================================================================

def get_user_by_email(db: Session, email: str) -> models.User | None:
    """
    Recipe to find a user by their email address.
    This is essential for checking if a user already exists during registration
    and for finding the user during login.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Recipe for creating a new user. This is a transactional process that
    creates both the main User record and their associated UserAuth record.
    """
    # 1. Hash the plain-text password from the request. We never store it directly.
    hashed_password = security.get_password_hash(user.password)

    # 2. Create the main User object, but *without* the password.
    # We now handle the name more flexibly.
    db_user = models.User(
        email=user.email,
        name=user.name or "New User" # Use the provided name or default to "New User"
    )
    db.add(db_user)
    # The 'flush' is like a pre-commit. It sends the user to the database so it gets an ID,
    # but it doesn't finalize the transaction yet. We need that ID for the UserAuth record.
    db.flush()

    # 3. Create the separate UserAuth object with the user's new ID and hashed password.
    db_user_auth = models.UserAuth(
        user_id=db_user.id,
        password_hash=hashed_password
    )
    db.add(db_user_auth)
    
    # 4. We do NOT commit here. The API endpoint that calls this function is responsible
    # for the final `db.commit()`. This allows us to group multiple operations
    # into a single, safe transaction. If something fails later, the endpoint can
    # roll back *all* of these changes.
    
    return db_user

# =============================================================================
# WEBSITE CRUD OPERATIONS (NEW)
# =============================================================================

def get_websites_by_user(db: Session, user_id: int) -> list[models.Website]:
    """Fetches all websites owned by a user"""
    return db.query(models.Website).filter(models.Website.user_id == user_id).all()

def create_website(db: Session, website: schemas.WebsiteCreate, user_id: int) -> models.Website:
    """
    Creates a new Website record, ensuring it is linked to a user.
    The user_id is a mandatory "ingredient" to enforce ownership.
    """
    db_website = models.Website(
        **website.model_dump(),  # Unpacks the 'url' and 'name' from the schema
        user_id=user_id          # Explicitly sets the owner
    )
    db.add(db_website)
    # The endpoint will handle the commit.
    return db_website

# =============================================================================
# CONNECTION CRUD OPERATIONS (NEW)
# =============================================================================

def get_website_by_id_and_owner(db: Session, website_id: int, user_id: int) -> models.Website | None:
    """
    Fetches a website only if it belongs to the specified user.
    This is a critical security function to ensure ownership.
    """
    return db.query(models.Website).filter(
        models.Website.id == website_id,
        models.Website.user_id == user_id
    ).first()

def create_connection_for_website(db: Session, connection: schemas.ConnectionCreate, website_id: int) -> models.Connection:
    """
    Creates a new Connection record and links it to a specific website.
    """
    db_connection = models.Connection(
        **connection.model_dump(), # Unpacks platform and platform_identifiers
        website_id=website_id      # Links it to the parent website
    )
    db.add(db_connection)
    return db_connection
