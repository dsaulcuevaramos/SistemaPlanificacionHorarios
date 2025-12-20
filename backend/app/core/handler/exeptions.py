# backend/app/core/exceptions.py

class BaseAppException(Exception):
    """Excepción base para errores lógicos del sistema"""
    pass

class CruceHorarioError(BaseAppException):
    """Se lanza cuando intentas programar una clase sobre otra"""
    def __init__(self, mensaje: str = "Existe un cruce de horarios"):
        self.mensaje = mensaje

class DocenteNoDisponibleError(BaseAppException):
    """Se lanza cuando el docente ya tiene clase en ese turno"""
    def __init__(self, docente_nombre: str):
        self.mensaje = f"El docente {docente_nombre} no tiene disponibilidad en este horario"

class RecursoNoEncontradoError(BaseAppException):
    """Para cuando buscas un ID que no existe"""
    def __init__(self, recurso: str, id: int):
        self.mensaje = f"{recurso} con id {id} no encontrado"