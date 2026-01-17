import pandas as pd
import random

import pandas as pd
import random

class GeneradorHorario:
    def __init__(self, df_sesiones, df_bloques, horarios_ocupados=None, bloques_reales_por_turno=None):
        self.df = df_sesiones.copy()
        self.bloques = df_bloques
        self.bloques_por_turno = bloques_reales_por_turno or {} # { id_turno: [orden1, orden2...] }
        
        # Sets para búsqueda rápida
        self.ocupacion_docente = set() 
        self.ocupacion_grupo = set()   
        
        # Cargar ocupación existente
        if horarios_ocupados:
            for h in horarios_ocupados:
                dia = h['dia']
                bloque = h['id_bloque']
                if h.get('id_docente'):
                    self.ocupacion_docente.add((h['id_docente'], dia, bloque))
                if h.get('grupo_uid'):
                    self.ocupacion_grupo.add((str(h['grupo_uid']), dia, bloque))

    def obtener_bloques_validos(self, id_turno):
        """
        Devuelve la lista EXACTA de bloques (orden) que tiene este turno en la BD.
        Ya no adivinamos por nombre.
        """
        if id_turno in self.bloques_por_turno:
            return self.bloques_por_turno[id_turno]
        
        # Fallback: Si no hay info, devuelve todo (riesgoso pero evita crash)
        return sorted(self.bloques['orden'].unique())

    def hay_cruce(self, id_docente, grupo_uid, dia, id_bloque):
        # Cruce Docente
        if id_docente and id_docente != "VACANTE":
            if (id_docente, dia, id_bloque) in self.ocupacion_docente:
                return True
        # Cruce Grupo
        if (str(grupo_uid), dia, id_bloque) in self.ocupacion_grupo:
            return True
        return False

    def reservar(self, id_docente, grupo_uid, dia, id_bloque):
        if id_docente:
            self.ocupacion_docente.add((id_docente, dia, id_bloque))
        self.ocupacion_grupo.add((str(grupo_uid), dia, id_bloque))

    def ejecutar(self):
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        
        # Ordenar por dificultad (Clases largas primero)
        self.df.sort_values(by=['DURACION_HORAS'], ascending=False, inplace=True)
        
        sesiones_sin_asignar = []

        for idx, row in self.df.iterrows():
            asignado = False
            grupo_uid = row.get('GRUPO_UID')
            id_turno = row['ID_TURNO']  # <--- AHORA USAMOS ID
            duracion = int(row['DURACION_HORAS'])
            id_docente = row['ID_DOCENTE']
            
            # Obtener bloques reales de la BD para este turno
            bloques_inicio_posibles = self.obtener_bloques_validos(id_turno)
            
            # Si el turno no tiene bloques (ej: error en BD), saltar
            if not bloques_inicio_posibles:
                print(f"⚠️ El Turno ID {id_turno} no tiene bloques registrados en la BD.")
                sesiones_sin_asignar.append(row['ID_SESION'])
                continue

            random.shuffle(dias_semana)

            for dia in dias_semana:
                if asignado: break
                
                for b_inicio in bloques_inicio_posibles:
                    bloques_necesarios = [b_inicio + i for i in range(duracion)]
                    
                    es_posible = True
                    for b in bloques_necesarios:
                        # 1. Validar que el bloque EXISTA en el turno (fundamental para tu caso)
                        if b not in bloques_inicio_posibles: 
                            es_posible = False; break
                        
                        # 2. Validar cruces
                        if self.hay_cruce(id_docente, grupo_uid, dia, b):
                            es_posible = False; break
                    
                    if es_posible:
                        # Asignar
                        self.df.at[idx, 'DIA'] = dia
                        self.df.at[idx, 'BLOQUE_ORDEN'] = b_inicio
                        
                        for b in bloques_necesarios:
                            self.reservar(id_docente, grupo_uid, dia, b)
                        
                        asignado = True
                        break
            
            if not asignado:
                sesiones_sin_asignar.append(row['ID_SESION'])

        return self.df, sesiones_sin_asignar