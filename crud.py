from sqlalchemy.orm import Session

# We import our models (the database blueprint), schemas (the API contract),
# and security functions (the locksmith).
from . import models, schemas, security

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
    db_user = models.User(
        name=user.name,
        email=user.email
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
