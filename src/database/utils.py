from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, exc
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session, sessionmaker

from src.settings import settings


def get_db_engine():
    """
    Cria e retorna uma engine do SQLAlchemy para conexão com o banco de dados.

    Returns:
        Engine: O engine do SQLAlchemy para a conexão com o banco de dados.
    """
    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD.get_secret_value(),
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
    )
    return create_engine(database_url, pool_size=10, max_overflow=20, pool_recycle=3600)


SessionLocal = sessionmaker()


@contextmanager
def create_db_connection(
    engine,
    autocommit=False,
    **session_opts,
) -> Generator[Session, None, None]:
    """
    Gerenciador de contexto que fornece uma sessão para interagir com o banco de dados.

    Args:
        engine (Engine): O engine do SQLAlchemy para a conexão com o banco de dados.
        autocommit (bool, optional): Se True, efetiva automaticamente as mudanças ao final do bloco.
                                     Se False, o usuário precisa chamar session.commit() explicitamente.
                                     Default é False.

    Yields:
        Session: Uma sessão do SQLAlchemy conectada ao banco de dados.

    Usage:
        with create_db_connection(engine) as session:  # Usa o padrão (autocommit=False)
            # Faça operações com a sessão aqui

        with create_db_connection(engine, autocommit=True) as session:
            # Faça operações com a sessão aqui e as mudanças serão efetivadas automaticamente
    """
    session = SessionLocal(bind=engine)
    try:
        yield session
        if autocommit:
            session.commit()
    except exc.SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()
