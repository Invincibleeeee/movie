import os
import pickle
import asyncio
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI, HTTPException, Query, Depends, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import JWTError, jwt


# =========================
# ENV
# =========================
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Auth secrets — set these in your .env file
SECRET_KEY       = os.getenv("SECRET_KEY", "change-me-in-production-use-openssl-rand-hex-32")
ALGORITHM        = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))  # 24h default

TMDB_BASE    = "https://api.themoviedb.org/3"
TMDB_IMG_500 = "https://image.tmdb.org/t/p/w500"

if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY missing. Put it in .env as TMDB_API_KEY=xxxx")

MONGO_URI = os.getenv("MONGO_URI", "")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI missing. Put it in .env as MONGO_URI=mongodb+srv://...")

# ── MongoDB connection ──
mongo_client = AsyncIOMotorClient(MONGO_URI)
mongo_db = mongo_client["recommendation"]
users_col = mongo_db["users"]
ratings_col = mongo_db["movies"]


# =========================
# FASTAPI APP
# =========================
app = FastAPI(title="Movie Recommender API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# AUTH INFRASTRUCTURE
# =========================

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme — tokenUrl must match our login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# In-memory user store is REPLACED by MongoDB (users_col)
# USERS_DB is no longer used


# ── Pydantic models for auth ──

class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class UserOut(BaseModel):
    username: str
    email: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


class TokenData(BaseModel):
    username: Optional[str] = None


# ── Helpers ──

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user(username: str) -> Optional[Dict[str, Any]]:
    # Kept as sync wrapper — only used inside authenticate_user
    # For async usage, use get_user_async
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Can't call sync from async context, use get_user_async instead
            return None
    except RuntimeError:
        pass
    return None


async def get_user_async(username: str) -> Optional[Dict[str, Any]]:
    doc = await users_col.find_one({"username": username})
    if doc:
        return {"hashed_password": doc["hashed_password"], "email": doc.get("email")}
    return None


async def authenticate_user_async(username: str, password: str) -> Optional[Dict[str, Any]]:
    user = await get_user_async(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[str]:
    """
    Returns the username from a valid JWT token, or None if no token / invalid.
    Use `get_current_user_required` for endpoints that must be authenticated.
    """
    if token is None:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None


async def get_current_user_required(token: str = Depends(oauth2_scheme)) -> str:
    """
    Strict version — raises 401 if not authenticated.
    Use this on protected endpoints.
    """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await get_user_async(username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# =========================
# PICKLE GLOBALS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DF_PATH          = os.path.join(BASE_DIR, "df.pkl")
INDICES_PATH     = os.path.join(BASE_DIR, "indices.pkl")
TFIDF_MATRIX_PATH = os.path.join(BASE_DIR, "tfidf_matrix.pkl")
TFIDF_PATH       = os.path.join(BASE_DIR, "tfidf.pkl")

df: Optional[pd.DataFrame]   = None
indices_obj: Any              = None
tfidf_matrix: Any             = None
tfidf_obj: Any                = None
TITLE_TO_IDX: Optional[Dict[str, int]] = None


# =========================
# PYDANTIC MODELS (unchanged)
# =========================
class TMDBMovieCard(BaseModel):
    tmdb_id: int
    title: str
    poster_url: Optional[str]    = None
    release_date: Optional[str]  = None
    vote_average: Optional[float] = None


class TMDBMovieDetails(BaseModel):
    tmdb_id: int
    title: str
    overview: Optional[str]      = None
    release_date: Optional[str]  = None
    poster_url: Optional[str]    = None
    backdrop_url: Optional[str]  = None
    genres: List[dict]           = []


class TFIDFRecItem(BaseModel):
    title: str
    score: float
    tmdb: Optional[TMDBMovieCard] = None


class SearchBundleResponse(BaseModel):
    query: str
    movie_details: TMDBMovieDetails
    tfidf_recommendations: List[TFIDFRecItem]
    genre_recommendations: List[TMDBMovieCard]


# =========================
# UTILS (unchanged)
# =========================
def _norm_title(t: str) -> str:
    return str(t).strip().lower()


def make_img_url(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    return f"{TMDB_IMG_500}{path}"


# Reusable httpx client (avoids creating a new TCP connection per request)
_httpx_client: httpx.AsyncClient | None = None

async def _get_httpx_client() -> httpx.AsyncClient:
    global _httpx_client
    if _httpx_client is None or _httpx_client.is_closed:
        _httpx_client = httpx.AsyncClient(timeout=30)
    return _httpx_client


async def tmdb_get(path: str, params: Dict[str, Any], _retries: int = 3) -> Dict[str, Any]:
    q = dict(params)
    q["api_key"] = TMDB_API_KEY
    last_err = None
    for attempt in range(1, _retries + 1):
        try:
            client = await _get_httpx_client()
            r = await client.get(f"{TMDB_BASE}{path}", params=q)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:  # rate-limited
                await asyncio.sleep(1.5 * attempt)
                continue
            raise HTTPException(status_code=502, detail=f"TMDB error {r.status_code}: {r.text[:200]}")
        except httpx.RequestError as e:
            last_err = e
            if attempt < _retries:
                await asyncio.sleep(1.0 * attempt)
                # Reset client on connection failure
                _httpx_client = None
                continue
    raise HTTPException(status_code=502, detail=f"TMDB unreachable after {_retries} attempts: {type(last_err).__name__}")


async def tmdb_cards_from_results(results: List[dict], limit: int = 20) -> List[TMDBMovieCard]:
    out: List[TMDBMovieCard] = []
    for m in (results or [])[:limit]:
        out.append(TMDBMovieCard(
            tmdb_id=int(m["id"]),
            title=m.get("title") or m.get("name") or "",
            poster_url=make_img_url(m.get("poster_path")),
            release_date=m.get("release_date"),
            vote_average=m.get("vote_average"),
        ))
    return out


async def tmdb_movie_details(movie_id: int) -> TMDBMovieDetails:
    data = await tmdb_get(f"/movie/{movie_id}", {"language": "en-US"})
    return TMDBMovieDetails(
        tmdb_id=int(data["id"]),
        title=data.get("title") or "",
        overview=data.get("overview"),
        release_date=data.get("release_date"),
        poster_url=make_img_url(data.get("poster_path")),
        backdrop_url=make_img_url(data.get("backdrop_path")),
        genres=data.get("genres", []) or [],
    )


async def tmdb_search_movies(query: str, page: int = 1) -> Dict[str, Any]:
    return await tmdb_get("/search/movie", {
        "query": query,
        "include_adult": "false",
        "language": "en-US",
        "page": page,
    })


async def tmdb_search_first(query: str) -> Optional[dict]:
    data = await tmdb_search_movies(query=query, page=1)
    results = data.get("results", [])
    return results[0] if results else None


# =========================
# TF-IDF Helpers (unchanged)
# =========================
def build_title_to_idx_map(indices: Any) -> Dict[str, int]:
    title_to_idx: Dict[str, int] = {}
    if isinstance(indices, dict):
        for k, v in indices.items():
            title_to_idx[_norm_title(k)] = int(v)
        return title_to_idx
    try:
        for k, v in indices.items():
            title_to_idx[_norm_title(k)] = int(v)
        return title_to_idx
    except Exception:
        raise RuntimeError("indices.pkl must be dict or pandas Series-like (with .items())")


def get_local_idx_by_title(title: str) -> int:
    global TITLE_TO_IDX
    if TITLE_TO_IDX is None:
        raise HTTPException(status_code=500, detail="TF-IDF index map not initialized")
    key = _norm_title(title)
    if key in TITLE_TO_IDX:
        return int(TITLE_TO_IDX[key])
    raise HTTPException(status_code=404, detail=f"Title not found in local dataset: '{title}'")


def tfidf_recommend_titles(query_title: str, top_n: int = 10) -> List[Tuple[str, float]]:
    global df, tfidf_matrix
    if df is None or tfidf_matrix is None:
        raise HTTPException(status_code=500, detail="TF-IDF resources not loaded")
    idx    = get_local_idx_by_title(query_title)
    qv     = tfidf_matrix[idx]
    scores = (tfidf_matrix @ qv.T).toarray().ravel()
    order  = np.argsort(-scores)
    out: List[Tuple[str, float]] = []
    for i in order:
        if int(i) == int(idx):
            continue
        try:
            title_i = str(df.iloc[int(i)]["title"])
        except Exception:
            continue
        out.append((title_i, float(scores[int(i)])))
        if len(out) >= top_n:
            break
    return out


async def attach_tmdb_card_by_title(title: str) -> Optional[TMDBMovieCard]:
    try:
        m = await tmdb_search_first(title)
        if not m:
            return None
        return TMDBMovieCard(
            tmdb_id=int(m["id"]),
            title=m.get("title") or title,
            poster_url=make_img_url(m.get("poster_path")),
            release_date=m.get("release_date"),
            vote_average=m.get("vote_average"),
        )
    except Exception:
        return None


# =========================
# STARTUP
# =========================
@app.on_event("startup")
def load_pickles():
    global df, indices_obj, tfidf_matrix, tfidf_obj, TITLE_TO_IDX

    with open(DF_PATH, "rb") as f:
        df = pickle.load(f)
    with open(INDICES_PATH, "rb") as f:
        indices_obj = pickle.load(f)
    with open(TFIDF_MATRIX_PATH, "rb") as f:
        tfidf_matrix = pickle.load(f)
    with open(TFIDF_PATH, "rb") as f:
        tfidf_obj = pickle.load(f)

    TITLE_TO_IDX = build_title_to_idx_map(indices_obj)

    if df is None or "title" not in df.columns:
        raise RuntimeError("df.pkl must contain a DataFrame with a 'title' column")


# =========================
# AUTH ROUTES  (/auth/*)
# =========================

@app.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegister):
    """
    Register a new user. Stored in MongoDB.
    """
    username = body.username.strip().lower()
    if not username or not body.password:
        raise HTTPException(status_code=400, detail="Username and password are required.")
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")
    if len(body.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")
    existing = await users_col.find_one({"username": username})
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken.")

    await users_col.insert_one({
        "username": username,
        "hashed_password": hash_password(body.password),
        "email": body.email,
        "created_at": datetime.utcnow(),
    })
    return UserOut(username=username, email=body.email)


@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with username + password (standard OAuth2 form).
    Returns a Bearer JWT token.
    """
    user = await authenticate_user_async(form_data.username.strip().lower(), form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        data={"sub": form_data.username.strip().lower()},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=token, token_type="bearer", username=form_data.username.strip().lower())


@app.get("/auth/me", response_model=UserOut)
async def get_me(current_user: str = Depends(get_current_user_required)):
    """
    Returns the currently authenticated user's profile.
    """
    user = await get_user_async(current_user)
    return UserOut(username=current_user, email=user.get("email") if user else None)


@app.post("/auth/logout")
async def logout(current_user: str = Depends(get_current_user_required)):
    return {"detail": f"Goodbye, {current_user}. Discard your token on the client."}


# =========================
# RATING ROUTES  (/ratings/*)
# =========================

class RatingIn(BaseModel):
    tmdb_id: int
    rating: int  # 1-5
    title: str = ""
    poster_url: Optional[str] = None


class RatingOut(BaseModel):
    tmdb_id: int
    rating: int
    title: str
    poster_url: Optional[str] = None
    rated_at: Optional[str] = None


@app.post("/ratings", response_model=RatingOut)
async def save_rating(body: RatingIn, current_user: str = Depends(get_current_user_required)):
    """Save or update a movie rating for the logged-in user."""
    if body.rating < 1 or body.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    now = datetime.utcnow()
    await ratings_col.update_one(
        {"username": current_user, "tmdb_id": body.tmdb_id},
        {"$set": {
            "username": current_user,
            "tmdb_id": body.tmdb_id,
            "rating": body.rating,
            "title": body.title,
            "poster_url": body.poster_url,
            "rated_at": now,
        }},
        upsert=True,
    )
    return RatingOut(
        tmdb_id=body.tmdb_id, rating=body.rating,
        title=body.title, poster_url=body.poster_url,
        rated_at=now.isoformat(),
    )


@app.get("/ratings", response_model=List[RatingOut])
async def get_ratings(current_user: str = Depends(get_current_user_required)):
    """Get all ratings for the logged-in user."""
    cursor = ratings_col.find({"username": current_user}).sort("rated_at", -1)
    results = []
    async for doc in cursor:
        results.append(RatingOut(
            tmdb_id=doc["tmdb_id"],
            rating=doc["rating"],
            title=doc.get("title", ""),
            poster_url=doc.get("poster_url"),
            rated_at=doc["rated_at"].isoformat() if doc.get("rated_at") else None,
        ))
    return results


@app.delete("/ratings/{tmdb_id}")
async def delete_rating(tmdb_id: int, current_user: str = Depends(get_current_user_required)):
    """Remove a rating."""
    result = await ratings_col.delete_one({"username": current_user, "tmdb_id": tmdb_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Rating not found")
    return {"detail": "Rating deleted"}


@app.get("/recommend/from-ratings")
async def recommend_from_ratings(
    limit: int = Query(18, ge=1, le=50),
    current_user: str = Depends(get_current_user_required),
):
    """
    Recommend movies based on user's rated movies.
    Uses TMDB /movie/{id}/recommendations — fast, 1 API call per rated movie.
    """
    # Get user's top-rated movies (prefer higher ratings)
    cursor = ratings_col.find(
        {"username": current_user, "rating": {"$gte": 3}}
    ).sort("rating", -1).limit(8)

    rated_docs = []
    async for doc in cursor:
        rated_docs.append(doc)

    if not rated_docs:
        raise HTTPException(status_code=404, detail="Rate some movies first to get recommendations!")

    rated_ids = {doc["tmdb_id"] for doc in rated_docs if doc.get("tmdb_id")}
    cards: List[TMDBMovieCard] = []
    seen_ids: set = set()

    # Fetch TMDB recommendations for each rated movie (parallel)
    async def _fetch_recs(tmdb_id: int) -> List[TMDBMovieCard]:
        try:
            data = await tmdb_get(f"/movie/{tmdb_id}/recommendations", {"language": "en-US", "page": 1})
            return await tmdb_cards_from_results(data.get("results", []), limit=20)
        except Exception:
            return []

    tasks = [_fetch_recs(doc["tmdb_id"]) for doc in rated_docs if doc.get("tmdb_id")]
    results = await asyncio.gather(*tasks)

    for result_cards in results:
        for card in result_cards:
            if card.tmdb_id not in seen_ids and card.tmdb_id not in rated_ids:
                cards.append(card)
                seen_ids.add(card.tmdb_id)
                if len(cards) >= limit:
                    break
        if len(cards) >= limit:
            break

    if not cards:
        raise HTTPException(status_code=404, detail="Could not generate recommendations. Try rating more movies!")

    return cards[:limit]


# =========================
# EXISTING ROUTES (unchanged)
# =========================

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/home", response_model=List[TMDBMovieCard])
async def home(
    category: str = Query("popular"),
    limit: int = Query(24, ge=1, le=50),
):
    try:
        if category == "trending":
            data = await tmdb_get("/trending/movie/day", {"language": "en-US"})
            return await tmdb_cards_from_results(data.get("results", []), limit=limit)
        if category not in {"popular", "top_rated", "upcoming", "now_playing"}:
            raise HTTPException(status_code=400, detail="Invalid category")
        data = await tmdb_get(f"/movie/{category}", {"language": "en-US", "page": 1})
        return await tmdb_cards_from_results(data.get("results", []), limit=limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Home route failed: {e}")


@app.get("/tmdb/search")
async def tmdb_search(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1, le=10),
):
    return await tmdb_search_movies(query=query, page=page)


@app.get("/movie/id/{tmdb_id}", response_model=TMDBMovieDetails)
async def movie_details_route(tmdb_id: int):
    return await tmdb_movie_details(tmdb_id)


@app.get("/recommend/genre", response_model=List[TMDBMovieCard])
async def recommend_genre(
    tmdb_id: int = Query(...),
    limit: int = Query(18, ge=1, le=50),
):
    details = await tmdb_movie_details(tmdb_id)
    if not details.genres:
        return []
    genre_id = details.genres[0]["id"]
    discover = await tmdb_get("/discover/movie", {
        "with_genres": genre_id,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "page": 1,
    })
    cards = await tmdb_cards_from_results(discover.get("results", []), limit=limit)
    return [c for c in cards if c.tmdb_id != tmdb_id]


@app.get("/recommend/tfidf")
async def recommend_tfidf(
    title: str = Query(..., min_length=1),
    top_n: int = Query(10, ge=1, le=50),
):
    recs = tfidf_recommend_titles(title, top_n=top_n)
    return [{"title": t, "score": s} for t, s in recs]


@app.get("/movie/search", response_model=SearchBundleResponse)
async def search_bundle(
    query: str = Query(..., min_length=1),
    tfidf_top_n: int = Query(12, ge=1, le=30),
    genre_limit: int = Query(12, ge=1, le=30),
):
    best = await tmdb_search_first(query)
    if not best:
        raise HTTPException(status_code=404, detail=f"No TMDB movie found for query: {query}")

    tmdb_id = int(best["id"])
    details = await tmdb_movie_details(tmdb_id)

    tfidf_items: List[TFIDFRecItem] = []
    recs: List[Tuple[str, float]] = []
    try:
        recs = tfidf_recommend_titles(details.title, top_n=tfidf_top_n)
    except Exception:
        try:
            recs = tfidf_recommend_titles(query, top_n=tfidf_top_n)
        except Exception:
            recs = []

    for title, score in recs:
        card = await attach_tmdb_card_by_title(title)
        tfidf_items.append(TFIDFRecItem(title=title, score=score, tmdb=card))

    genre_recs: List[TMDBMovieCard] = []
    if details.genres:
        genre_id = details.genres[0]["id"]
        discover = await tmdb_get("/discover/movie", {
            "with_genres": genre_id,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "page": 1,
        })
        cards = await tmdb_cards_from_results(discover.get("results", []), limit=genre_limit)
        genre_recs = [c for c in cards if c.tmdb_id != details.tmdb_id]

    return SearchBundleResponse(
        query=query,
        movie_details=details,
        tfidf_recommendations=tfidf_items,
        genre_recommendations=genre_recs,
    )