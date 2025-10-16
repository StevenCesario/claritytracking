from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

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
    Normalizes email to lowercase and strips whitespace for consistency.
    """
    normalized_email = email.strip().lower()
    return db.query(models.User).filter(models.User.email == normalized_email).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Recipe for creating a new user. This is a transactional process that
    creates both the main User record and their associated UserAuth record.
    Normalizes email and name before creation.
    """
    # 1. Hash the plain-text password from the request. We never store it directly.
    hashed_password = security.get_password_hash(user.password)

    # 2. Create the main User object, but *without* the password.
    # We now handle the name more flexibly.
    db_user = models.User(
        email=user.email.strip().lower(),
        name=(user.name or "New User").strip() # Use the provided name or default to "New User"
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
# WEBSITE CRUD OPERATIONS
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
# CONNECTION CRUD OPERATIONS
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

# =============================================================================
# WAITLIST CRUD OPERATIONS
# =============================================================================

def create_or_get_waitlist_entry(db: Session, data: schemas.WaitlistCreate, ip_address: str, user_agent: str) -> tuple[models.Waitlist, bool]:
    """
    Creates a new waitlist entry or retrieves it if the email already exists.
    Returns the waitlist object and a boolean indicating if it was created.
    """
    normalized_email = data.email.strip().lower()
    
    # Check if the user already exists first.
    existing_entry = db.query(models.Waitlist).filter(models.Waitlist.email == normalized_email).first()
    if existing_entry:
        return existing_entry, False # Return existing entry, was not created

    # Create a new entry if one doesn't exist.
    new_entry = models.Waitlist(
        email=normalized_email,
        source=data.source,
        utm_source=data.utm_source,
        utm_medium=data.utm_medium,
        utm_campaign=data.utm_campaign,
        referer=data.referer,
        ip_address=ip_address[:64], # Truncate to prevent errors
        user_agent=(user_agent or "")[:512], # Truncate and handle None
    )
    db.add(new_entry)
    
    try:
        db.commit()
        db.refresh(new_entry)
        return new_entry, True # Return new entry, was created
    except IntegrityError:
        # This is a race condition failsafe: if two requests come in at the exact same
        # time, the second one will fail the unique constraint. We roll back and
        # fetch the one that was just created by the other request.
        db.rollback()
        existing_entry = db.query(models.Waitlist).filter(models.Waitlist.email == normalized_email).first()
        # The unique constraint means another request must have created the entry;
        # assert for the type checker that existing_entry is not None.
        assert existing_entry is not None
        return existing_entry, False