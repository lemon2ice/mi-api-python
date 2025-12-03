from app.database import db
import os
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserModel:
    @staticmethod
    def create_default_admin():
        """Crea un usuario admin por defecto si no existe"""
        try:
            # Verificar si ya existe un admin
            query = "SELECT id FROM users WHERE email = %s"
            existing_user = db.fetch_one(query, (os.getenv("DEFAULT_ADMIN_EMAIL"),))
            
            if not existing_user:
                # Crear usuario admin
                hashed_password = pwd_context.hash(os.getenv("DEFAULT_ADMIN_PASSWORD"))
                query = """
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
                """
                db.execute_query(query, (
                    "Administrador",
                    os.getenv("DEFAULT_ADMIN_EMAIL"),
                    hashed_password,
                    "admin"
                ))
                print("Usuario admin creado por defecto")
        except Exception as e:
            print(f"Error creando usuario admin: {e}")
    
    @staticmethod
    def get_user_by_email(email: str):
        """Obtiene un usuario por su email"""
        query = "SELECT * FROM users WHERE email = %s"
        return db.fetch_one(query, (email,))
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str):
        """Verifica si la contraseña coincide con el hash"""
        return pwd_context.verify(plain_password, hashed_password)

class BookModel:
    @staticmethod
    def create_book(book_data: dict):
        """Crea un nuevo libro"""
        query = """
        INSERT INTO books (title, isbn, publication_year, price, stock, cover_image_url)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor = db.execute_query(query, (
            book_data['title'],
            book_data.get('isbn'),
            book_data.get('publication_year'),
            book_data.get('price', 0),
            book_data.get('stock', 0),
            book_data.get('cover_image_url')
        ))
        return cursor.lastrowid
    
    @staticmethod
    def get_all_books():
        """Obtiene todos los libros con sus autores"""
        query = """
        SELECT b.*, 
               GROUP_CONCAT(a.name ORDER BY a.name SEPARATOR ', ') as authors,
               GROUP_CONCAT(a.id ORDER BY a.name SEPARATOR ',') as author_ids
        FROM books b
        LEFT JOIN book_authors ba ON b.id = ba.book_id
        LEFT JOIN authors a ON ba.author_id = a.id
        GROUP BY b.id
        ORDER BY b.title
        """
        books = db.fetch_all(query)
        # Convertir author_ids de cadena a lista
        for book in books:
            if book.get('author_ids'):
                # Convertir "1,2,3" a [1, 2, 3]
                book['author_ids'] = [
                    int(aid.strip()) 
                    for aid in book['author_ids'].split(',') 
                    if aid.strip()
                ]
            else:
                book['author_ids'] = []
        return books
    
    @staticmethod
    def get_book_by_id(book_id: int):
        """Obtiene un libro por su ID con sus autores"""
        query = """
        SELECT b.*, 
               GROUP_CONCAT(a.name ORDER BY a.name SEPARATOR ', ') as authors,
               GROUP_CONCAT(a.id ORDER BY a.name SEPARATOR ',') as author_ids
        FROM books b
        LEFT JOIN book_authors ba ON b.id = ba.book_id
        LEFT JOIN authors a ON ba.author_id = a.id
        WHERE b.id = %s
        GROUP BY b.id
        """
        book = db.fetch_one(query, (book_id,))
        if book:
            print(f"DEBUG get_book_by_id: author_ids tipo: {type(book.get('author_ids'))}, valor: {book.get('author_ids')}")
            
            # Asegurar que author_ids sea una lista
            ids_value = book.get('author_ids')
            if ids_value and isinstance(ids_value, str):
                # Convertir cadena "1,2,3" a lista [1, 2, 3]
                book['author_ids'] = [
                    int(aid.strip()) 
                    for aid in ids_value.split(',') 
                    if aid.strip()
                ]
            elif ids_value is None or ids_value == '':
                # Si es None o cadena vacía, establecer lista vacía
                book['author_ids'] = []
            elif isinstance(ids_value, list):
                # Si ya es lista, dejarla como está
                pass
            else:
                # Para cualquier otro caso (números, etc.), convertir a lista
                try:
                    book['author_ids'] = [int(ids_value)]
                except:
                    book['author_ids'] = []
        else:
            book = None
            
        return book
    
    @staticmethod
    def update_book(book_id: int, book_data: dict):
        """Actualiza un libro existente"""
        print(f"DEBUG: En BookModel.update_book - ID: {book_id}, datos: {book_data}")
        
        # Construir la consulta dinámicamente
        fields = []
        values = []
        
        for field in ['title', 'isbn', 'publication_year', 'price', 'stock', 'cover_image_url']:
            if field in book_data and book_data[field] is not None:
                fields.append(f"{field} = %s")
                values.append(book_data[field])
        
        print(f"DEBUG: Campos a actualizar: {fields}")
        print(f"DEBUG: Valores: {values}")
        
        if not fields:
            print("DEBUG: No hay campos para actualizar")
            return False
        
        values.append(book_id)
        query = f"UPDATE books SET {', '.join(fields)} WHERE id = %s"
        
        print(f"DEBUG: Query: {query}")
        print(f"DEBUG: Parámetros: {values}")
        
        try:
            db.execute_query(query, tuple(values))
            print("DEBUG: Libro actualizado exitosamente en la base de datos")
            return True
        except Exception as e:
            print(f"ERROR: Error ejecutando query: {str(e)}")
            raise
    
    @staticmethod
    def delete_book(book_id: int):
        """Elimina un libro por su ID"""
        query = "DELETE FROM books WHERE id = %s"
        db.execute_query(query, (book_id,))
        return True
    
    @staticmethod
    def add_author_to_book(book_id: int, author_id: int):
        """Asocia un autor a un libro"""
        try:
            query = "INSERT INTO book_authors (book_id, author_id) VALUES (%s, %s)"
            db.execute_query(query, (book_id, author_id))
            return True
        except Exception as e:
            print(f"Error añadiendo autor al libro: {e}")
            return False
    
    @staticmethod
    def remove_author_from_book(book_id: int, author_id: int):
        """Elimina la asociación de un autor con un libro"""
        query = "DELETE FROM book_authors WHERE book_id = %s AND author_id = %s"
        db.execute_query(query, (book_id, author_id))
        return True

class AuthorModel:
    @staticmethod
    def get_all_authors():
        """Obtiene todos los autores"""
        query = "SELECT * FROM authors ORDER BY name"
        return db.fetch_all(query)
    
    @staticmethod
    def get_author_by_id(author_id: int):
        """Obtiene un autor por su ID"""
        query = "SELECT * FROM authors WHERE id = %s"
        return db.fetch_one(query, (author_id,))