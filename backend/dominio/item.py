"""Item: una línea del carrito de compras."""

from __future__ import annotations

from itertools import count

from .manejador_reglas import ManejadorReglas
from .producto import Producto
from .reglas import ReglaPrecio

_secuencia_ids = count(1)


class Item:
    """Clase `Item` del diagrama.

    Un ítem asocia un producto con una cantidad y con la regla de precio que le
    corresponde. La regla se resuelve UNA sola vez, en el constructor, usando
    `ManejadorReglas` (la dependencia punteada del diagrama).

    A partir de ese momento el ítem solo conoce la interfaz `ReglaPrecio`: no
    sabe si el producto es normal, de peso o de descuento especial. Por eso
    `calcular_total` nunca necesita cambiar cuando se agrega una regla nueva.
    """

    def __init__(
        self,
        producto: Producto,
        cantidad: int,
        manejador_reglas: ManejadorReglas | None = None,
    ) -> None:
        self.producto = producto
        self.cantidad = cantidad
        manejador = manejador_reglas or ManejadorReglas()
        self.regla_precio: ReglaPrecio = manejador.obtener_regla(producto.sku)
        # Identificador técnico. No está en el diagrama: se agrega para poder
        # referenciar el ítem desde el frontend a través de HTTP.
        self.id = next(_secuencia_ids)

    def calcular_total(self) -> float:
        """Valor total de la línea, delegado por completo a la regla de precio."""
        return self.regla_precio.calcular_total(
            self.cantidad, self.producto.precio_unitario
        )

    def agregar_cantidad(self, cantidad: int) -> None:
        """Suma `cantidad` a la línea existente.

        Se usa cuando el mismo producto se agrega dos veces al carrito, para
        que la regla de precio (p. ej. el descuento por bloques) se calcule
        sobre la cantidad total y no quede fragmentada en varias líneas.
        """
        self.cantidad += cantidad

    def __repr__(self) -> str:  # pragma: no cover - only for debugging
        return f"Item(sku={self.producto.sku!r}, cantidad={self.cantidad})"
