#modulo auth 
from app.models.base import Base, BaseMixin
from app.models.escuela import Escuela
from app.models.usuario import Usuario
from app.models.catalogo import Catalogo

# modulo cursos y todo lo relacionado
from app.models.plan_estudio import PlanEstudio
from app.models.plan_version import PlanVersion
from app.models.curso import Curso

from app.models.docente import Docente
from app.models.contrato_docente import ContratoDocente
from app.models.disponibilidad_docente import DisponibilidadDocente

from app.models.aula import Aula  
from app.models.turno import Turno
from app.models.bloque_horario import BloqueHorario


from .periodo_academico import PeriodoAcademico
from .grupo import Grupo
from .horario import Horario
from .horario_examen import HorarioExamen 
from .sesion import Sesion 
# ... (y así sucesivamente con todos los modelos)