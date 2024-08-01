# database.py

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Tạo một lớp cơ sở cho các định nghĩa lớp khai báo
Base = declarative_base()

# Định nghĩa lớp User với các trường cần thiết
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    userid = Column(Integer, unique=True, nullable=False)
    api_key = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(username={self.username}, userid={self.userid}, api_key={self.api_key})>"

# Khởi tạo cơ sở dữ liệu SQLite
engine = create_engine('sqlite:///users.db', echo=True)

# Tạo bảng users nếu chưa tồn tại
Base.metadata.create_all(engine)

# Tạo một session factory
SessionLocal = sessionmaker(bind=engine)

# Hàm để lấy một session mới
def get_session():
    return SessionLocal()
