from sqlalchemy import create_engine, delete, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase,Session
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String,DateTime
from typing import List
from typing import Optional
from uuid_extensions import uuid7
from enum import Enum
from datetime import datetime

engine = create_engine("sqlite+pysqlite:///data.sqlite", echo=True)


class Base(DeclarativeBase):
    pass


print(Base.metadata)


class CsvRequest(Base):
    __tablename__ = "csv_request"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_guid: Mapped[str] = mapped_column(String(50))
    filename: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30))
    images : Mapped[List["ImageItem"]] = relationship(back_populates="csv_request")
    created_on : Mapped[datetime] = mapped_column(DateTime)
    
    def __repr__(self) -> str:
        return f"User: {self.id}, filename:{self.filename}, request_guid:{self.request_guid}, status:{self.status}"

class ImageItem(Base):
    __tablename__ = "request_images"
    id: Mapped[int] = mapped_column(primary_key=True)
    image_guid: Mapped[str] = mapped_column(String(50))
    image_name: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50))
    input_url: Mapped[str] = mapped_column(String(50))
    output_url: Mapped[str] = mapped_column(String(50),nullable=True)
    item_index : Mapped[str] = mapped_column(String(200))
    csv_request_id = mapped_column(ForeignKey("csv_request.id"))
    
    csv_request: Mapped[CsvRequest] = relationship(back_populates="images")

Base.metadata.create_all(engine)

class CsvRequestStatus(Enum):
    UPLOADED = "UPLOADED"
    PARTIAL = "PARTIAL"
    COMPLETED = "COMPLETED"
    
class ImageItemStatus(Enum):
    PENDING = "PENDING"
    FAILED  = "FAILED"
    PROCESSED = "PROCESSED"
    INVALID = "INVALID"


Engine = None

def get_db_engine():
    global Engine
    if Engine != None:
        return Engine
    else:
        Engine = create_engine("sqlite+pysqlite:///../data.sqlite", echo=True)
        return Engine
    
def get_db_session():
    engine = get_db_engine()
    session = Session(engine)
    return session
