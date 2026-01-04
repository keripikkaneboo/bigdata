from sqlalchemy import create_engine, text
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

def get_engine(with_db=True):
    """
    Membuat engine SQLAlchemy.
    with_db=False digunakan saat awal pembuatan database.
    """
    if with_db:
        url = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        url = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
    
    return create_engine(url)