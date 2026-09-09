"""Esquemas Pydantic: representación de las entidades del dominio en la API.

Se mantienen separados de las clases del dominio a propósito. Las clases del
dominio tienen comportamiento (métodos de negocio); estos esquemas son solo
estructuras de datos para serializar hacia el frontend. Mezclarlos ataría el
modelo de objetos al formato de transporte.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ProductoOut(BaseModel):
    sku: str
    nombre: str
    descripcion: str
    unidades_disponibles: int
    precio_unitario: float
    tipo: str = Field(description="Nombre de la regla de precio aplicable")
    unidad: str = Field(description="Unidad en que se expresa la cantidad")


class ItemOut(BaseModel):
    id: int
    sku: str
    nombre: str
    cantidad: int
    precio_unitario: float
    regla: str
    total: float


class CarritoOut(BaseModel):
    items: List[ItemOut]
    total: float


class AgregarItemIn(BaseModel):
    sku: str
    cantidad: int = Field(gt=0, description="Unidades (o kilogramos, para WE)")


class TiendaOut(BaseModel):
    total_ventas: float


class CompraOut(BaseModel):
    total: float
    total_ventas: float
