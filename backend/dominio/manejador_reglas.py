"""ManejadorReglas: selecciona la regla de precio que aplica a un SKU."""

from __future__ import annotations

from typing import List

from .reglas import ReglaPrecio, ReglaPrecioPorDefecto, reglas_registradas


class ManejadorReglas:
    """Clase `ManejadorReglas` del diagrama.

    Mantiene la colección de reglas disponibles (`reglas`) y resuelve, para un
    SKU dado, cuál de ellas debe usarse. Es el único punto del sistema que
    conoce el conjunto completo de reglas; el resto de las clases solo conoce
    la interfaz `ReglaPrecio`.
    """

    def __init__(self, reglas: List[ReglaPrecio] | None = None) -> None:
        # Por defecto se instancian todas las reglas inscritas con
        # @registrar_regla. Se permite inyectar una lista propia para pruebas
        # o para configuraciones alternativas de la tienda.
        self.reglas: List[ReglaPrecio] = (
            reglas if reglas is not None else [cls() for cls in reglas_registradas()]
        )
        self._regla_por_defecto = ReglaPrecioPorDefecto()

    def obtener_regla(self, sku: str) -> ReglaPrecio:
        """Retorna la primera regla que se declara aplicable al SKU."""
        for regla in self.reglas:
            if regla.es_aplicable(sku):
                return regla
        return self._regla_por_defecto
