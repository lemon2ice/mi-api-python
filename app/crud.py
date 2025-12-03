from fastapi import HTTPException, status
from typing import List, Optional

from app.models import BookModel, AuthorModel
from app.schemas import BookCreate, BookUpdate, BookResponse, AuthorResponse

class BookCRUD:
    @staticmethod
    def create_book(book_data: BookCreate):
        """Crea un nuevo libro"""
        try:
            # Convertir Pydantic model a dict
            book_dict = book_data.dict(exclude={'author_ids'})
            
            # Crear el libro
            book_id = BookModel.create_book(book_dict)
            
            # Asociar autores si se proporcionaron
            if book_data.author_ids:
                for author_id in book_data.author_ids:
                    # Verificar que el autor existe
                    author = AuthorModel.get_author_by_id(author_id)
                    if author:
                        BookModel.add_author_to_book(book_id, author_id)
            
            # Obtener el libro creado
            created_book = BookModel.get_book_by_id(book_id)
            return created_book
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creando el libro: {str(e)}"
            )
    
    @staticmethod
    def get_books():
        """Obtiene todos los libros"""
        try:
            books = BookModel.get_all_books()
            return books
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error obteniendo libros: {str(e)}"
            )
    
    @staticmethod
    def get_book(book_id: int):
        """Obtiene un libro por ID"""
        book = BookModel.get_book_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Libro no encontrado"
            )
        return book
    
    @staticmethod
    def update_book(book_id: int, book_data: BookUpdate):
        """Actualiza un libro existente"""
        print(f"DEBUG: Actualizando libro {book_id} con datos: {book_data.dict()}")
        
        # Verificar que el libro existe
        existing_book = BookModel.get_book_by_id(book_id)
        if not existing_book:
            print(f"DEBUG: Libro {book_id} no encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Libro no encontrado"
            )
        
        print(f"DEBUG: Libro existente author_ids tipo: {type(existing_book.get('author_ids'))}")
        print(f"DEBUG: Libro existente author_ids valor: {existing_book.get('author_ids')}")
        
        try:
            # Filtrar campos no nulos
            update_data = {k: v for k, v in book_data.dict(exclude={'author_ids'}).items() if v is not None}
            
            print(f"DEBUG: Datos a actualizar: {update_data}")
            
            if update_data:
                BookModel.update_book(book_id, update_data)
            
            # Manejar autores si se proporcionaron
            if book_data.author_ids is not None:
                print(f"DEBUG: Procesando autores: {book_data.author_ids}")
                
                # Obtener author_ids como lista (asegurarse de que sea una lista)
                existing_author_ids = existing_book.get('author_ids', [])
                
                # Si es string, convertir a lista
                if isinstance(existing_author_ids, str):
                    existing_author_ids = [
                        int(id_str.strip()) 
                        for id_str in existing_author_ids.split(',') 
                        if id_str.strip()
                    ]
                # Si es None, establecer lista vacía
                elif existing_author_ids is None:
                    existing_author_ids = []
                # Si ya es lista, dejarla como está
                elif not isinstance(existing_author_ids, list):
                    existing_author_ids = []
                
                print(f"DEBUG: IDs de autores existentes (como lista): {existing_author_ids}")
                
                # Primero, eliminar todas las asociaciones existentes
                if existing_author_ids:
                    print(f"DEBUG: Eliminando asociaciones existentes")
                    for author_id in existing_author_ids:
                        BookModel.remove_author_from_book(book_id, author_id)
                
                # Luego, agregar los nuevos autores (si la lista no está vacía)
                if book_data.author_ids:
                    print(f"DEBUG: Agregando nuevos autores")
                    for author_id in book_data.author_ids:
                        author = AuthorModel.get_author_by_id(author_id)
                        if author:
                            BookModel.add_author_to_book(book_id, author_id)
                        else:
                            print(f"WARN: Autor {author_id} no encontrado, omitiendo")
                else:
                    # Si book_data.author_ids es una lista vacía, significa eliminar todos los autores
                    print(f"DEBUG: Lista de autores vacía - eliminando todas las asociaciones")
            
            # Retornar el libro actualizado
            updated_book = BookModel.get_book_by_id(book_id)
            print(f"DEBUG: Libro actualizado: {updated_book}")
            return updated_book
        except Exception as e:
            print(f"ERROR: Excepción en update_book: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error actualizando el libro: {str(e)}"
            )
    
    @staticmethod
    def delete_book(book_id: int):
        """Elimina un libro"""
        # Verificar que el libro existe
        existing_book = BookModel.get_book_by_id(book_id)
        if not existing_book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Libro no encontrado"
            )
        
        try:
            BookModel.delete_book(book_id)
            return {"message": "Libro eliminado exitosamente"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error eliminando el libro: {str(e)}"
            )

class AuthorCRUD:
    @staticmethod
    def get_authors():
        """Obtiene todos los autores"""
        try:
            authors = AuthorModel.get_all_authors()
            return authors
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error obteniendo autores: {str(e)}"
            )
    
    @staticmethod
    def get_author(author_id: int):
        """Obtiene un autor por ID"""
        author = AuthorModel.get_author_by_id(author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Autor no encontrado"
            )
        return author