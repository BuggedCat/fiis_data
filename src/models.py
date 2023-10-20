from datetime import date, datetime
from decimal import Decimal
from typing import Self
from xml.etree.ElementTree import Element

from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

from src.utils import (
    clean_text,
    convert_xml_element_to_dict,
    find_xml_tag,
    parse_date_string,
)

Datetime = Annotated[datetime, BeforeValidator(parse_date_string)]
Date = Annotated[date, BeforeValidator(parse_date_string)]
CNPJ = Annotated[str, BeforeValidator(clean_text)]


class DadosGerais(BaseModel):
    nome_fundo: str = Field(alias="NomeFundo")
    cnpj_fundo: CNPJ = Field(alias="CNPJFundo")
    nome_administrador: str = Field(alias="NomeAdministrador")
    cnpj_administrador: CNPJ = Field(alias="CNPJAdministrador")
    responsavel_informacao: str = Field(alias="ResponsavelInformacao")
    telefone_contato: str = Field(alias="TelefoneContato")
    cod_isin_cota: str = Field(alias="CodISINCota")
    cod_negociacao_cota: str = Field(alias="CodNegociacaoCota")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @classmethod
    def from_xml(cls, root: Element) -> Self:
        dados_gerais_et = find_xml_tag(root, "DadosGerais")

        xml_dict = convert_xml_element_to_dict(dados_gerais_et)

        return cls.model_validate(xml_dict)


class Rendimento(BaseModel):
    ato_societario_aprovacao: str | None = Field(
        alias="AtoSocietarioAprovacao",
        default=None,
    )
    data_aprovacao: Datetime | None = Field(
        alias="DataAprovacao",
        default=None,
    )
    data_base: Datetime = Field(alias="DataBase")
    data_pagamento: Datetime = Field(alias="DataPagamento")
    valor_provento_cota: Decimal = Field(alias="ValorProventoCota")
    periodo_referencia: str = Field(alias="PeriodoReferencia")
    ano: str = Field(alias="Ano")
    rendimento_isento_ir: bool = Field(alias="RendimentoIsentoIR")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @classmethod
    def from_xml(cls, root: Element) -> Self | None:
        informe_rendimentos_et = find_xml_tag(root, "InformeRendimentos")
        try:
            rendimento_et = find_xml_tag(informe_rendimentos_et, "Rendimento")
            xml_dict = convert_xml_element_to_dict(rendimento_et)

            if not xml_dict:
                return None

            return cls.model_validate(xml_dict)
        except KeyError:
            return None


class Amortizacao(BaseModel):
    ato_societario_aprovacao: str | None = Field(
        alias="AtoSocietarioAprovacao",
        default=None,
    )
    data_aprovacao: Datetime | None = Field(
        alias="DataAprovacao",
        default=None,
    )
    data_base: Datetime = Field(alias="DataBase")
    data_pagamento: Datetime = Field(alias="DataPagamento")
    valor_provento_cota: Decimal = Field(alias="ValorProventoCota")
    periodo_referencia: str = Field(alias="PeriodoReferencia")
    ano: int = Field(alias="Ano")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @classmethod
    def from_xml(cls, root: Element) -> Self | None:
        informe_rendimentos_et = find_xml_tag(root, "InformeRendimentos")
        try:
            amortizacao_et = find_xml_tag(informe_rendimentos_et, "Amortizacao")
            xml_dict = convert_xml_element_to_dict(amortizacao_et)

            if not xml_dict:
                return None

            return cls.model_validate(xml_dict)
        except KeyError:
            return None


class InformeRendimentos(BaseModel):
    amortizacao: Amortizacao | None = Field(default=None)
    rendimento: Rendimento | None = Field(default=None)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @classmethod
    def from_xml(cls, root: Element) -> Self:
        return cls(
            amortizacao=Amortizacao.from_xml(root),
            rendimento=Rendimento.from_xml(root),
        )


class DadosEconomicoFinanceiros(BaseModel):
    dados_gerais: DadosGerais
    informe_rendimentos: InformeRendimentos

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @classmethod
    def from_xml(cls, root: Element):
        return cls(
            dados_gerais=DadosGerais.from_xml(root),
            informe_rendimentos=InformeRendimentos.from_xml(root),
        )


class DataItem(BaseModel):
    id: int = Field(alias="id")
    descricao_fundo: str = Field(alias="descricaoFundo")
    categoria_documento: str = Field(alias="categoriaDocumento")
    tipo_documento: str = Field(alias="tipoDocumento")
    data_referencia: Date = Field(alias="dataReferencia")
    data_entrega: Datetime = Field(alias="dataEntrega")
    status: str = Field(alias="status")
    descricao_status: str = Field(alias="descricaoStatus")
    analisado: str = Field(alias="analisado")
    situacao_documento: str = Field(alias="situacaoDocumento")
    alta_prioridade: bool = Field(alias="altaPrioridade")
    formato_data_referencia: str = Field(alias="formatoDataReferencia")
    versao: int = Field(alias="versao")
    modalidade: str = Field(alias="modalidade")
    descricao_modalidade: str = Field(alias="descricaoModalidade")
    nome_pregao: str = Field(alias="nomePregao")
    informacoes_adicionais: str = Field(alias="informacoesAdicionais")
    id_template: int = Field(alias="idTemplate")
    id_select_item_convenio: int = Field(alias="idSelectItemConvenio")
    indicador_fundo_ativo_b3: bool = Field(alias="indicadorFundoAtivoB3")

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class APIResponse(BaseModel):
    draw: int
    records_filtered: int = Field(alias="recordsFiltered")
    records_total: int = Field(alias="recordsTotal")
    data: list[DataItem]

    model_config = ConfigDict(extra="forbid", populate_by_name=True)
