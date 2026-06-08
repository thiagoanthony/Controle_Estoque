from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id             = Column(Integer, primary_key=True, index=True)
    nome           = Column(String, nullable=False)
    categoria      = Column(String, nullable=False)
    quantidade     = Column(Integer, nullable=False, default=0)
    estoque_minimo = Column(Integer, nullable=False, default=0)
    preco          = Column(Float, nullable=False, default=0.0)


class MensagemChat(Base):
    __tablename__ = "historico_chat"

    id           = Column(Integer, primary_key=True, index=True)
    role         = Column(String, nullable=False)        # "user" ou "ai"
    texto        = Column(Text, nullable=False)
    bloqueado    = Column(Boolean, default=False)
    camada       = Column(Integer, nullable=True)
    similaridade = Column(Float, nullable=True)
    criado_em    = Column(DateTime, server_default=func.now())
