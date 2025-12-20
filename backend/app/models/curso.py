from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin # O donde tengas definido tu Mixin

# Tabla intermedia para requisitos (Many-to-Many)
# Nota: El nombre interno de la tabla es 'curso_requisito'
curso_requisito_assoc = Table(
    'curso_requisito',
    Base.metadata,
    Column('id_curso', Integer, ForeignKey('curso.id'), primary_key=True),
    Column('id_curso_requisito', Integer, ForeignKey('curso.id'), primary_key=True),
    Column('id_plan_version', Integer, ForeignKey('plan_version.id')) # Opcional
)

class Curso(Base, BaseMixin):
    __tablename__ = 'curso'
    
    codigo = Column(String(20))
    nombre = Column(String(150))
    ciclo = Column(Integer)
    paridad = Column(String(10))
    creditos = Column(Integer)
    horas_teoricas = Column(Integer)
    horas_practicas = Column(Integer)
    tipo_curso = Column(String(20))

    id_plan_version = Column(Integer, ForeignKey("plan_version.id")) 
    
    # Relaciones
    plan_version = relationship("PlanVersion", back_populates="cursos")
    aperturas = relationship("CursoAperturado", back_populates="curso")

    # RELACIÓN DE PRE-REQUISITOS (Self-referential)
    # CORRECCIÓN: Usamos strings para definir los joins explícitamente.
    # 'curso_requisito' refiere al nombre de la tabla definida arriba en Table('curso_requisito', ...)
    requisitos = relationship(
        "Curso",
        secondary=curso_requisito_assoc,
        primaryjoin="Curso.id == curso_requisito.c.id_curso",
        secondaryjoin="Curso.id == curso_requisito.c.id_curso_requisito",
        backref="es_requisito_de"
    )