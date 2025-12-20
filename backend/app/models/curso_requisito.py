from sqlalchemy import Column, Integer, Date, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

class ContratoDocente(Base, BaseMixin):
    __tablename__ = "curso_requisito" # Nombre explícito

    id_cruso = Column(Integer, ForeignKey("curso.id")) 
    id_cruso_requisito = Column(Integer, ForeignKey("curso.id")) 
    id_plan_version = Column(Integer, ForeignKey("plan_version.id")) 
    tipo_requisto = Column(String(50))
 

