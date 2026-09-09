"""Errores del dominio.

Se definen excepciones propias para que la capa de dominio no dependa de
FastAPI ni de HTTP: la capa web las traduce a códigos de estado.
"""


class ErrorDominio(Exception):
    """Error de negocio previsible (se reporta al usuario, no es un bug)."""


class ProductoNoEncontrado(ErrorDominio):
    pass


class ItemNoEncontrado(ErrorDominio):
    pass


class CantidadInvalida(ErrorDominio):
    pass


class InventarioInsuficiente(ErrorDominio):
    pass


class CarritoVacio(ErrorDominio):
    pass
