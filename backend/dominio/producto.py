"""Producto: entidad central del catálogo de la tienda.

Corresponde a la clase `Producto` del diagrama de diseño del OVA.
"""

from __future__ import annotations


class Producto:
    """Un producto del catálogo de la tienda.

    Atributos (tal como aparecen en el diagrama):
        sku: código del producto. Su prefijo codifica el tipo de producto
             (EA = normal, WE = por peso, SP = descuento especial).
        nombre: nombre comercial del producto.
        descripcion: descripción corta del producto.
        unidades_disponibles: inventario disponible.
        precio_unitario: precio por unidad. Para los productos de peso (WE)
             este precio está expresado por GRAMO, no por kilogramo.

    Nota de diseño: `Producto` no sabe nada sobre cómo se calculan los precios.
    Esa responsabilidad vive por completo en las implementaciones de
    `ReglaPrecio`, de modo que agregar o cambiar reglas no obliga a tocar
    esta clase.
    """

    def __init__(
        self,
        sku: str,
        nombre: str,
        descripcion: str,
        unidades_disponibles: int,
        precio_unitario: float,
    ) -> None:
        self.sku = sku
        self.nombre = nombre
        self.descripcion = descripcion
        self.unidades_disponibles = unidades_disponibles
        self.precio_unitario = precio_unitario

    def tiene_unidades(self, cantidad: int) -> bool:
        """Indica si hay inventario suficiente para la cantidad solicitada."""
        return cantidad > 0 and self.unidades_disponibles >= cantidad

    def descontar_unidades(self, cantidad: int) -> None:
        """Descuenta del inventario las unidades vendidas.

        Se invoca únicamente al concretar la compra (ver `Tienda.finalizar_compra`).
        """
        if not self.tiene_unidades(cantidad):
            raise ValueError(
                f"No hay unidades suficientes de {self.sku}: "
                f"disponibles {self.unidades_disponibles}, solicitadas {cantidad}"
            )
        self.unidades_disponibles -= cantidad

    def __repr__(self) -> str:  # pragma: no cover - only for debugging
        return f"Producto(sku={self.sku!r}, nombre={self.nombre!r})"
