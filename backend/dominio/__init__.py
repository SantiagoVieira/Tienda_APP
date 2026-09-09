"""Capa de dominio: implementación directa del diseño orientado a objetos.

Este paquete no importa nada de FastAPI ni de la capa web. Cada clase del
diagrama del OVA está en su propio módulo:

    Producto              -> producto.py
    ReglaPrecio (+3 impl) -> reglas.py
    ManejadorReglas       -> manejador_reglas.py
    Item                  -> item.py
    Carrito               -> carrito.py
    Usuario               -> usuario.py
    Tienda                -> tienda.py
"""

from .carrito import Carrito
from .errores import (
    CantidadInvalida,
    CarritoVacio,
    ErrorDominio,
    InventarioInsuficiente,
    ItemNoEncontrado,
    ProductoNoEncontrado,
)
from .item import Item
from .manejador_reglas import ManejadorReglas
from .producto import Producto
from .reglas import (
    ReglaPrecio,
    ReglaPrecioEspecial,
    ReglaPrecioNormal,
    ReglaPrecioPorPeso,
    registrar_regla,
)
from .tienda import Tienda
from .usuario import Usuario

__all__ = [
    "Carrito",
    "CantidadInvalida",
    "CarritoVacio",
    "ErrorDominio",
    "InventarioInsuficiente",
    "Item",
    "ItemNoEncontrado",
    "ManejadorReglas",
    "Producto",
    "ProductoNoEncontrado",
    "ReglaPrecio",
    "ReglaPrecioEspecial",
    "ReglaPrecioNormal",
    "ReglaPrecioPorPeso",
    "Tienda",
    "Usuario",
    "registrar_regla",
]
