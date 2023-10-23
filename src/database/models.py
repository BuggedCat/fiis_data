from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from src.validators import FnetDocumento

Base = declarative_base()


class FnetDocumentoModel(Base):
    __tablename__ = "fnet_documento"

    pk_id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, nullable=False)
    descricao_fundo = Column(String, nullable=False)
    categoria_documento = Column(String, nullable=False)
    tipo_documento = Column(String, nullable=False)
    data_referencia = Column(Date, nullable=False)
    data_entrega = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    descricao_status = Column(String, nullable=False)
    analisado = Column(String, nullable=False)
    situacao_documento = Column(String, nullable=False)
    alta_prioridade = Column(Boolean)
    formato_data_referencia = Column(String, nullable=False)
    versao = Column(Integer, nullable=False)
    modalidade = Column(String, nullable=False)
    descricao_modalidade = Column(String, nullable=False)
    nome_pregao = Column(String, nullable=False)
    informacoes_adicionais = Column(String, nullable=False)
    id_template = Column(Integer, nullable=False)
    id_select_item_convenio = Column(Integer, nullable=False)
    indicador_fundo_ativo_b3 = Column(Boolean, nullable=False)
    inserted_at = Column(DateTime, default=func.now())
    last_update = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("document_id", "data_referencia", name="uq_document_data_ref"),
    )


def upsert_fnet_documento(session: Session, document: FnetDocumento) -> CursorResult:
    data = document.model_dump()
    statement = (
        insert(FnetDocumentoModel)
        .values(**data)
        .on_conflict_do_update(
            constraint="uq_document_data_ref",
            set_={**data, "last_update": func.now()},
        )
    )
    return session.execute(statement)


def fetch_last_document_date(session: Session) -> datetime | None:
    aggregation = func.max(FnetDocumentoModel.data_entrega)
    query = session.query(aggregation)
    result = query.scalar()
    return result


def fetch_documents_ids(session: Session, exclude_ids: list[int] | None = None):
    query = session.query(FnetDocumentoModel.document_id)
    if exclude_ids:
        query = query.filter(FnetDocumentoModel.document_id.not_in(exclude_ids))
    yield from query.yield_per(1000)
