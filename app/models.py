from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    num_pages = Column(Integer)
    chunks = relationship('Chunk', back_populates='document')

class Chunk(Base):
    __tablename__ = 'chunks'
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    chunk_index = Column(Integer)
    text = Column(String)
    embedding_id = Column(String)  # Reference to vector DB
    document = relationship('Document', back_populates='chunks')
