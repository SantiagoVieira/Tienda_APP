"""Tienda: fachada del dominio y dueña del inventario y las ventas."""

from __future__ import annotations

from typing import Dict, List

from .errores import (
    CantidadInvalida,
    CarritoVacio,
    InventarioInsuficiente,
    ItemNoEncontrado,
    ProductoNoEncontrado,
)
from .item import Item
from .manejador_reglas import ManejadorReglas
from .producto import Producto
from .usuario import Usuario


class Tienda:
    """Clase `Tienda` del diagrama.

    Es el punto de entrada del dominio: agrupa los productos y los usuarios, y
    expone las tres operaciones de negocio del caso de estudio. La API REST se
    limita a traducir peticiones HTTP a llamados sobre esta clase.
    """

    def __init__(
        self,
        productos: List[Producto] | None = None,
        manejador_reglas: ManejadorReglas | None = None,
    ) -> None:
        self.total_ventas: float = 0.0
        self.productos: List[Producto] = productos or []
        self.usuarios: Dict[str, Usuario] = {}
        # El manejador se crea una sola vez y se comparte con los carritos.
        self.manejador_reglas = manejador_reglas or ManejadorReglas()

    # -- Consultas -----------------------------------------------------------

    def buscar_producto(self, sku: str) -> Producto:
        producto = next(
            (p for p in self.productos if p.sku.upper() == sku.upper()), None
        )
        if producto is None:
            raise ProductoNoEncontrado(f"No existe el producto con SKU {sku}")
        return producto

    def obtener_usuario(self, nombre: str) -> Usuario:
        """Retorna el usuario, creándolo la primera vez que aparece."""
        if nombre not in self.usuarios:
            self.usuarios[nombre] = Usuario(nombre, self.manejador_reglas)
        return self.usuarios[nombre]

    def unidades_reservadas(self, usuario: Usuario, producto: Producto) -> int:
        """Unidades de un producto que el usuario ya tiene en su carrito."""
        return sum(
            item.cantidad
            for item in usuario.carrito.items
            if item.producto.sku == producto.sku
        )

    # -- Operaciones de negocio ---------------------------------------------

    def agregar_producto_a_carrito(
        self, usuario: Usuario, producto: Producto, cantidad: int
    ) -> Item:
        """Agrega un producto al carrito verificando disponibilidad.

        La verificación descuenta lo que el usuario ya tiene reservado en su
        carrito, de modo que no pueda agregar dos veces el inventario completo.
        El inventario real solo se modifica al concretar la compra.
        """
        if cantidad <= 0:
            raise CantidadInvalida("La cantidad debe ser mayor que cero")

        reservadas = self.unidades_reservadas(usuario, producto)
        if not producto.tiene_unidades(reservadas + cantidad):
            disponibles = max(producto.unidades_disponibles - reservadas, 0)
            raise InventarioInsuficiente(
                f"Solo quedan {disponibles} unidades disponibles de "
                f"{producto.nombre}"
            )

        return usuario.agregar_item_a_carrito(producto, cantidad)

    def eliminar_item_de_carrito(self, usuario: Usuario, item: Item) -> None:
        """Elimina un ítem del carrito del usuario."""
        try:
            usuario.borrar_item_de_carrito(item)
        except ValueError as exc:
            raise ItemNoEncontrado(str(exc)) from exc

    def finalizar_compra(self, usuario: Usuario) -> float:
        """Concreta la compra: acumula la venta y descuenta el inventario.

        Retorna el valor total de la venta. La operación se valida por completo
        antes de modificar nada, para no dejar el inventario a medio actualizar
        si un producto se agotó mientras el carrito estaba abierto.
        """
        carrito = usuario.carrito
        if not carrito.items:
            raise CarritoVacio("El carrito está vacío")

        requeridas: Dict[str, int] = {}
        for item in carrito.items:
            requeridas[item.producto.sku] = (
                requeridas.get(item.producto.sku, 0) + item.cantidad
            )
        for sku, cantidad in requeridas.items():
            producto = self.buscar_producto(sku)
            if not producto.tiene_unidades(cantidad):
                raise InventarioInsuficiente(
                    f"Ya no hay {cantidad} unidades de {producto.nombre}"
                )

        total = carrito.calcular_total()
        for sku, cantidad in requeridas.items():
            self.buscar_producto(sku).descontar_unidades(cantidad)

        self.total_ventas += total
        carrito.vaciar()
        return total
