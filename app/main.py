from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta

from app.database import db
from app.models import UserModel
from app.schemas import UserLogin, Token, BookCreate, BookUpdate, BookResponse, AuthorResponse
from app.auth import create_access_token, get_current_user, require_admin
from app.crud import BookCRUD, AuthorCRUD

app = FastAPI(title="Library API", description="API para gestión de biblioteca", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Evento de inicio: crear usuario admin por defecto
@app.on_event("startup")
async def startup_event():
    print("Iniciando aplicación...")
    # Conectar a la base de datos
    db.connect()
    # Crear usuario admin por defecto
    UserModel.create_default_admin()
    print("Aplicación lista")

# Evento de apagado
@app.on_event("shutdown")
async def shutdown_event():
    print("Cerrando aplicación...")
    db.disconnect()

# Rutas de autenticación
@app.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Endpoint para login de usuarios"""
    # Buscar usuario por email
    user = UserModel.get_user_by_email(user_credentials.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Verificar contraseña
    if not UserModel.verify_password(user_credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Rutas para libros (requieren autenticación)
@app.post("/books", response_model=BookResponse)
async def create_book(
    book: BookCreate,
    current_user = Depends(require_admin)
):
    """Crear un nuevo libro (solo admin)"""
    return BookCRUD.create_book(book)

@app.get("/books", response_model=list[BookResponse])
async def get_books(
    current_user = Depends(get_current_user)
):
    """Obtener todos los libros"""
    return BookCRUD.get_books()

@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    current_user = Depends(get_current_user)
):
    """Obtener un libro por ID"""
    return BookCRUD.get_book(book_id)

@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book: BookUpdate,
    current_user = Depends(require_admin)
):
    """Actualizar un libro (solo admin)"""
    return BookCRUD.update_book(book_id, book)

@app.delete("/books/{book_id}")
async def delete_book(
    book_id: int,
    current_user = Depends(require_admin)
):
    """Eliminar un libro (solo admin)"""
    return BookCRUD.delete_book(book_id)

# Rutas para autores (solo lectura)
@app.get("/authors", response_model=list[AuthorResponse])
async def get_authors(
    current_user = Depends(get_current_user)
):
    """Obtener todos los autores"""
    return AuthorCRUD.get_authors()

@app.get("/authors/{author_id}", response_model=AuthorResponse)
async def get_author(
    author_id: int,
    current_user = Depends(get_current_user)
):
    """Obtener un autor por ID"""
    return AuthorCRUD.get_author(author_id)

# Ruta de health check
@app.get("/health")
async def health_check():
    """Verificar el estado de la API"""
    try:
        # Intentar conectar a la base de datos
        connection = db.connect()
        if connection and connection.is_connected():
            db_status = "connected"
            db.disconnect()
        else:
            db_status = "disconnected"
    except Exception:
        db_status = "error"
    
    return {
        "status": "healthy",
        "database": db_status,
        "service": "Library API"
    }

# Ruta raíz
@app.get("/")
async def read_root():
    return {
        "message": "Bienvenido a la API de la Biblioteca",
        "docs": "/docs",
        "redoc": "/redoc"
    }