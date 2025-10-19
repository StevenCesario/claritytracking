from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

# Annotated as a modern way to declare dependencies, List for the response models
from typing import Annotated, List

# ---- Internal Imports ----
# We bring in all the pieces we've built so far.
from . import crud, models, schemas, security, database

# This command ensures our database tables are created based on our models.
# It's good practice to have it here, though Alembic is our primary tool for this.
models.Base.metadata.create_all(bind=database.engine)

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
    "https://claritypixel.io",      # Your future prod domain
    "https://www.claritypixel.io",
    # Add production frontend URL here later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.framer\.app$", # Allow Framer previews
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================

@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check():
    """A simple endpoint to confirm the API is running."""
    return {"status": "ok"}

# =============================================================================
# WAITLIST ENDPOINT
# =============================================================================

@app.post("/api/waitlist", response_model=schemas.WaitlistResponse)
def join_waitlist(
    payload: schemas.WaitlistCreate,
    request: Request,
    response: Response,
    db: Session = Depends(database.get_db)
):
    """Endpoint for users to join the waitlist."""
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    
    entry, created = crud.create_or_get_waitlist_entry(
        db=db, data=payload, ip_address=ip_address, user_agent=user_agent
    )

    # Use the 'created' variable to set the status code
    if created:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK
    
    return entry

# =============================================================================
# AUTHENTICATION ENDPOINTS
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

# =============================================================================
# USER & WEBSITE ENDPOINTS
# =============================================================================

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

@app.post("/api/websites", response_model=schemas.WebsiteResponse, status_code=status.HTTP_201_CREATED)
def create_website_for_user(
    website: schemas.WebsiteCreate,
    current_user: Annotated[models.User, Depends(security.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """
    Protected endpoint to create a new website for the logged-in user.
    """
    db_website = crud.create_website(db=db, website=website, user_id=current_user.id)
    db.commit()
    db.refresh(db_website)
    return db_website

@app.get("/api/websites", response_model=List[schemas.WebsiteResponse])
def read_websites_for_user(
    current_user: Annotated[models.User, Depends(security.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """
    Protected endpoint to retrieve all websites owned by the logged-in user.
    """
    websites = crud.get_websites_by_user(db=db, user_id=current_user.id)
    return websites

# =============================================================================
# CONNECTION ENDPOINTS
# =============================================================================

@app.post("/api/websites/{website_id}/connections", response_model=schemas.ConnectionResponse, status_code=status.HTTP_201_CREATED)
def create_connection(
    website_id: int,
    connection: schemas.ConnectionCreate,
    current_user: Annotated[models.User, Depends(security.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """
    Protected endpoint to create a new platform connection for a specific website.
    Crucially, it first verifies that the user owns the website.
    """
    # 1. Ownership Verification: Use our security-focused CRUD function.
    db_website = crud.get_website_by_id_and_owner(db=db, website_id=website_id, user_id=current_user.id)
    
    # 2. If the website doesn't exist or doesn't belong to the user, deny access.
    if db_website is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found or you do not have permission to access it."
        )
    
    # 3. If ownership is confirmed, proceed to create the connection.
    db_connection = crud.create_connection_for_website(db=db, connection=connection, website_id=website_id)
    db.commit()
    db.refresh(db_connection)
    return db_connection

# UPDATED: Now uses ingested data instead of mock data
@app.get("/api/websites/{website_id}/health", response_model=list[schemas.EventHealth])
def get_website_health(
    website_id: int,
    current_user: Annotated[models.User, Depends(security.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """
    Returns calculated event health data for a given website based on recent event logs.
    """
    # 1. Ownership check (critical for security)
    db_website = crud.get_website_by_id_and_owner(
        db=db,
        website_id=website_id,
        user_id=current_user.id,
    )
    if db_website is None: # FIX: Should be db_website, not website_id
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found or you do not have permission to access it."
        )
    
    # 2. UPDATED: Get the summary data from the database
    # Let's look back 3 days (72 hours) for relevant events
    summary_data = crud.get_recent_event_summary(db=db, website_id=website_id, time_window_hours=72)

    # 3. Process the summary to calculate status and mock EMQ
    health_results = []
    now = datetime.now(timezone.utc)

    # Define the standard events we care about for the monitor
    standard_events = ["PageView", "AddToCart", "InitiateCheckout", "Purchase"]

    # Create a dictionary for quick lookup
    summary_map = {item["event_name"]: item for item in summary_data}

    for event_name in standard_events:
        event_summary = summary_map.get(event_name)

        if event_summary:
            last_received = event_summary["last_received"]
            time_diff = now - last_received
            fbp_present = event_summary["fbp_present"]

            # Simple status logic based on recency
            if time_diff > timedelta(days=1):
                event_status = "error"
            elif time_diff > timedelta(hours=4): # Make warning threshold a bit shorter
                event_status = "warning"
            else:
                event_status = "healthy"

            # Very basic mock EMQ score calculation
            # Start with a base score, add points for recency and fbp
            emq_score = 4.0 
            if event_status == "healthy":
                emq_score += 3.0
            elif event_status == "warning":
                emq_score += 1.5
                
            if fbp_present: # Give points if fbp cookie was logged
                 emq_score += 2.1 
            
            # Cap the score at 9.9 for realism 
            emq_score = min(emq_score, 9.9)

            health_results.append(schemas.EventHealth(
                event_name=event_name,
                emq_score=emq_score,
                last_received=last_received,
                status=event_status
            ))
        else:
            # If the event hasn't been received in the time window
             health_results.append(schemas.EventHealth(
                event_name=event_name,
                emq_score=0.0, # No data, score is 0
                last_received=datetime.min.replace(tzinfo=timezone.utc), # Use minimum datetime
                status="error" # Mark as error if not seen recently
            ))
             
    return health_results

# NEW: Mock endpoint for health alerts
@app.get("/api/websites/{website_id}/alerts", response_model=list[schemas.EventAlert])
def get_website_alerts(
    website_id: int,
    current_user: Annotated[models.User, Depends(security.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """
    Returns mock health alerts for a given website.
    """
    # 1. Ownership check (critical for security)
    db_website = crud.get_website_by_id_and_owner(
        db=db,
        website_id=website_id,
        user_id=current_user.id,
    )
    if db_website is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found or you do not have permission to access it."
        )
    
    # 2. Return mock data (mismatched, duplicate)
    mock_alerts = [
        schemas.EventAlert(
            id="alert-1",
            severity="error",
            title="Duplicate 'Purchase' Events Detected",
            message="We are seeing multiple 'Purchase' events with the same event ID. This can inflate your conversion data in Meta Ads Manager.",
            timestamp=datetime.now(timezone.utc) - timedelta(hours=2)
        ),
        schemas.EventAlert(
            id="alert-2",
            severity="warning",
            title="'InitiateCheckout' EMQ is Low (6.2/10)",
            message="Your 'InitiateCheckout' events are missing key customer parameters. This can reduce ad performance and increase costs.",
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=45)
        )
    ]
    return mock_alerts