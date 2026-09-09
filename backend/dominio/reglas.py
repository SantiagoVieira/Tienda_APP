"""Reglas de cálculo de precio.

Este módulo contiene la interfaz `ReglaPrecio` del diagrama y sus tres
implementaciones concretas. Es el punto de extensión del sistema: agregar una
nueva regla de precio consiste en escribir una clase nueva en este archivo (o
en cualquier otro módulo) y decorarla con `@registrar_regla`. Ningún otro
componente de la aplicación necesita cambiar.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Type

# ---------------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------------


class ReglaPrecio(ABC):
    """Interfaz `ReglaPrecio` del diagrama.

    Define el contrato que toda regla de precio debe cumplir:

    * `es_aplicable(sku)`: la propia regla decide si le corresponde un SKU.
      Esto evita un `if/elif` centralizado que habría que modificar cada vez
      que aparece un tipo de producto nuevo.
    * `calcular_total(cantidad, precio)`: calcula el valor total de la línea.
    """

    #: Nombre legible de la regla, útil para mostrarla en la interfaz.
    nombre: str = "Regla de precio"

    #: Unidad en la que se expresa la cantidad para esta regla. La expone la
    #: propia regla (y no la capa web) para que el frontend pueda etiquetar
    #: correctamente un tipo de producto nuevo sin cambios en la API.
    unidad: str = "unidad"

    @abstractmethod
    def es_aplicable(self, sku: str) -> bool:
        """Retorna True si esta regla debe usarse para el SKU dado."""

    @abstractmethod
    def calcular_total(self, cantidad: int, precio: float) -> float:
        """Retorna el valor total a cobrar por `cantidad` a `precio` unitario."""


# ---------------------------------------------------------------------------
# Registro de reglas (mecanismo de extensión)
# ---------------------------------------------------------------------------

_REGLAS_REGISTRADAS: List[Type[ReglaPrecio]] = []


def registrar_regla(cls: Type[ReglaPrecio]) -> Type[ReglaPrecio]:
    """Decorador que inscribe una regla en el catálogo global de reglas.

    `ManejadorReglas` construye su lista a partir de este registro, de manera
    que una regla nueva queda disponible con solo declararla.
    """
    _REGLAS_REGISTRADAS.append(cls)
    return cls


def reglas_registradas() -> List[Type[ReglaPrecio]]:
    """Retorna las clases de regla registradas, en orden de declaración."""
    return list(_REGLAS_REGISTRADAS)


# ---------------------------------------------------------------------------
# Implementaciones concretas
# ---------------------------------------------------------------------------


@registrar_regla
class ReglaPrecioNormal(ReglaPrecio):
    """Producto normal (SKU que empieza por EA): precio unitario x cantidad."""

    nombre = "Producto normal"
    PREFIJO = "EA"

    def es_aplicable(self, sku: str) -> bool:
        return sku.upper().startswith(self.PREFIJO)

    def calcular_total(self, cantidad: int, precio: float) -> float:
        return precio * cantidad


@registrar_regla
class ReglaPrecioPorPeso(ReglaPrecio):
    """Producto de peso (SKU que empieza por WE).

    El precio unitario del producto está dado POR GRAMO y la cantidad se
    expresa en KILOGRAMOS, por lo que el total es:

        total = cantidad_kg * 1000 g/kg * precio_por_gramo
    """

    nombre = "Producto de peso"
    unidad = "kg"
    PREFIJO = "WE"
    GRAMOS_POR_KILOGRAMO = 1000

    def es_aplicable(self, sku: str) -> bool:
        return sku.upper().startswith(self.PREFIJO)

    def calcular_total(self, cantidad: int, precio: float) -> float:
        return cantidad * self.GRAMOS_POR_KILOGRAMO * precio


@registrar_regla
class ReglaPrecioEspecial(ReglaPrecio):
    """Producto de descuento especial (SKU que empieza por SP).

    Se aplica un 20% de descuento por cada 3 unidades completas, con un tope
    máximo de 50%. Es decir:

        3 a 5 unidades  -> 20%
        6 a 8 unidades  -> 40%
        9 o más         -> 50% (tope)
    """

    nombre = "Descuento especial"
    PREFIJO = "SP"
    UNIDADES_POR_DESCUENTO = 3
    DESCUENTO_POR_BLOQUE = 0.20
    DESCUENTO_MAXIMO = 0.50

    def es_aplicable(self, sku: str) -> bool:
        return sku.upper().startswith(self.PREFIJO)

    def calcular_total(self, cantidad: int, precio: float) -> float:
        bloques = cantidad // self.UNIDADES_POR_DESCUENTO
        descuento = min(bloques * self.DESCUENTO_POR_BLOQUE, self.DESCUENTO_MAXIMO)
        return precio * cantidad * (1 - descuento)


class ReglaPrecioPorDefecto(ReglaPrecio):
    """Regla de respaldo para SKUs cuyo prefijo no reconoce ninguna regla.

    No se registra en el catálogo: `ManejadorReglas` la usa explícitamente como
    último recurso para que el sistema nunca quede sin una forma de cotizar.
    """

    nombre = "Sin regla específica"

    def es_aplicable(self, sku: str) -> bool:
        return True

    def calcular_total(self, cantidad: int, precio: float) -> float:
        return precio * cantidad
