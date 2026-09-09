"""Carrito de compras."""

from __future__ import annotations

from typing import List

from .item import Item
from .manejador_reglas import ManejadorReglas
from .producto import Producto


class Carrito:
    """Clase `Carrito` del diagrama.

    Contiene una colección de `Item` (composición: los ítems no existen fuera
    del carrito) y sabe calcular el total de la compra sumando el total de cada
    línea. El carrito no conoce ninguna regla de precio.
    """

    def __init__(self, manejador_reglas: ManejadorReglas | None = None) -> None:
        self.items: List[Item] = []
        self._manejador_reglas = manejador_reglas or ManejadorReglas()

    def agregar_item(self, producto: Producto, cantidad: int) -> Item:
        """Crea y agrega una línea nueva al carrito, y la retorna."""
        item = Item(producto, cantidad, self._manejador_reglas)
        self.items.append(item)
        return item

    def calcular_total(self) -> float:
        """Suma del total de todas las líneas del carrito."""
        return sum(item.calcular_total() for item in self.items)

    def borrar_item(self, item: Item) -> None:
        """Elimina una línea del carrito."""
        if item not in self.items:
            raise ValueError("El ítem no pertenece a este carrito")
        self.items.remove(item)

    def buscar_item(self, item_id: int) -> Item | None:
        """Busca una línea por su identificador técnico.

        Método auxiliar de la implementación (no está en el diagrama): el
        frontend identifica los ítems por id al pedir su eliminación.
        """
        return next((i for i in self.items if i.id == item_id), None)

    def vaciar(self) -> None:
        """Deja el carrito sin ítems. Se usa al concretar la compra."""
        self.items.clear()
