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
        """Agrega `cantidad` del producto al carrito.

        Si el producto ya tiene una línea en el carrito, se suma la cantidad
        a esa línea existente en lugar de crear una nueva. Así la regla de
        precio (p. ej. el descuento por bloques) se calcula sobre la
        cantidad total del producto y no queda fragmentada en varias líneas.
        """
        item_existente = self._buscar_item_por_producto(producto)
        if item_existente is not None:
            item_existente.agregar_cantidad(cantidad)
            return item_existente

        item = Item(producto, cantidad, self._manejador_reglas)
        self.items.append(item)
        return item

    def _buscar_item_por_producto(self, producto: Producto) -> Item | None:
        return next(
            (i for i in self.items if i.producto.sku == producto.sku), None
        )

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
