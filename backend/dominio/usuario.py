"""Usuario de la tienda."""

from __future__ import annotations

from .carrito import Carrito
from .item import Item
from .manejador_reglas import ManejadorReglas
from .producto import Producto


class Usuario:
    """Clase `Usuario` del diagrama.

    Cada usuario tiene su propio carrito y delega en él las operaciones de
    agregar y borrar ítems.
    """

    def __init__(
        self, nombre: str, manejador_reglas: ManejadorReglas | None = None
    ) -> None:
        self.nombre = nombre
        self.carrito = Carrito(manejador_reglas)

    def agregar_item_a_carrito(self, producto: Producto, cantidad: int) -> Item:
        return self.carrito.agregar_item(producto, cantidad)

    def borrar_item_de_carrito(self, item: Item) -> None:
        self.carrito.borrar_item(item)
