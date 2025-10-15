from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Annotated # A modern way to declare dependencies

# ---- Internal Imports ----
# We bring in all the pieces we've built so far.
from . import crud, models, schemas, security, database

# Create the main FastAPI application instance. This is our "restaurant".
app = FastAPI(
    title="ClarityPixel API",
    description="The backend service for ClarityPixel, providing CAPI automation and attribution.",
    version="1.0.0"
)

# --- CORS Middleware ---
# This allows our frontend (running on a different domain like Vercel)
# to make requests to our backend.
origins = [
    "http://localhost:5173", # Default Vite dev server
    # Add your production frontend URL here later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.post("/api/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """
    Endpoint for new user registration.
    This is the "waiter" taking a new customer's order.
    """
    # 1. Check if a user with this email already exists by using our CRUD recipe.
    db_user = crud.get_user_by_email(db, email=user_data.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please log in instead."
        )
    
    # 2. If the user is new, use the `create_user` recipe from our recipe book.
    try:
        new_user = crud.create_user(db=db, user=user_data)
        # 3. This is where we finalize the transaction. If `create_user` was successful,
        # we commit both the User and UserAuth records to the database.
        db.commit()
        # Refresh the object to get the latest state from the database.
        db.refresh(new_user)
        return new_user
    except Exception as e:
        # If anything goes wrong during user creation, we roll back the entire transaction.
        # This ensures our database stays in a clean, consistent state.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user account: {str(e)}"
        )

@app.post("/api/login", response_model=schemas.TokenResponse)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(database.get_db)
):
    """
    Endpoint for user login.
    It verifies credentials and returns a JWT "keycard".
    """
    # 1. Find the user by their email using our CRUD recipe.
    # Note: OAuth2PasswordRequestForm uses 'username' for the email field.
    user = crud.get_user_by_email(db, email=form_data.username)

    # 2. Verify that the user exists and the password is correct using our security utility.
    if not user or not security.verify_password(form_data.password, user.auth.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. If credentials are valid, use our "Locksmith" to create a new JWT keycard.
    # The 'sub' (subject) of the token is the user's ID.
    access_token = security.create_access_token(data={"sub": str(user.id)})

    # 4. Return the token to the client.
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=schemas.UserResponse)
def get_user_me(current_user: Annotated[models.User, Depends(security.get_current_user)]):
    """
    A protected endpoint to get the current user's profile.
    The `get_current_user` dependency acts as the "Bouncer", ensuring only
    authenticated users can access this.
    """
    # If the code reaches this point, the bouncer has already done all the work:
    # validated the token and fetched the user from the database.
    # We can simply return the user object.
    return current_user
