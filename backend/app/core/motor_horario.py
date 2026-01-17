import pandas as pd
import random

class GeneradorHorario:
    def __init__(self, df_sesiones, df_bloques, df_aulas=None, horarios_ocupados=None):
        self.df = df_sesiones.copy()
        self.bloques = df_bloques
        
        # Sets para búsqueda ultrarrápida (O(1))
        self.ocupacion_docente = set() # (ID_DOCENTE, DIA, ID_BLOQUE)
        self.ocupacion_grupo = set()   # (GRUPO_UID, DIA, ID_BLOQUE)
        
        # --- CARGAR LO QUE YA EXISTE (MANUAL O DE OTROS CICLOS) ---
        if horarios_ocupados:
            for h in horarios_ocupados:
                dia = h['dia']
                bloque = h['id_bloque']

                # 1. Bloquear al Docente
                if h.get('id_docente'):
                    self.ocupacion_docente.add((h['id_docente'], dia, bloque))
                
                # 2. Bloquear al Grupo
                if h.get('grupo_uid'):
                    self.ocupacion_grupo.add((str(h['grupo_uid']), dia, bloque))

    def obtener_bloques_validos(self, turno_nombre):
        """
        Define qué números de bloque (orden) puede usar un turno.
        Asume: 1-6 (Mañana), 7-12 (Tarde), 13-18 (Noche)
        """
        todos_los_bloques = sorted(self.bloques['orden'].unique())
        nombre = str(turno_nombre).upper() # Normalizamos a mayúsculas para evitar errores
        
        bloques_permitidos = []

        # Lógica acumulativa (para turnos compuestos como 'MAÑANA Y TARDE' o 'TARDE - NOCHE')
        usar_manana = 'MAÑANA' in nombre or 'MANANA' in nombre
        usar_tarde = 'TARDE' in nombre
        usar_noche = 'NOCHE' in nombre

        # Si no detecta nada conocido (ej: "Turno Único"), usa todo
        if not (usar_manana or usar_tarde or usar_noche):
            return todos_los_bloques

        if usar_manana:
            bloques_permitidos.extend([b for b in todos_los_bloques if b <= 6])
        
        if usar_tarde:
            bloques_permitidos.extend([b for b in todos_los_bloques if b > 6 and b <= 12])
            
        if usar_noche:
            bloques_permitidos.extend([b for b in todos_los_bloques if b > 12])

        # Eliminamos duplicados y ordenamos
        return sorted(list(set(bloques_permitidos)))

    def hay_cruce(self, id_docente, grupo_uid, dia, id_bloque):
        # 1. Cruce Docente
        if id_docente and id_docente != "VACANTE":
            if (id_docente, dia, id_bloque) in self.ocupacion_docente:
                return True
        
        # 2. Cruce Grupo
        if (str(grupo_uid), dia, id_bloque) in self.ocupacion_grupo:
            return True
            
        return False

    def reservar(self, id_docente, grupo_uid, dia, id_bloque):
        if id_docente:
            self.ocupacion_docente.add((id_docente, dia, id_bloque))
        self.ocupacion_grupo.add((str(grupo_uid), dia, id_bloque))

    def ejecutar(self):
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        
        # Ordenamos: Primero las sesiones más largas (más difíciles de ubicar)
        self.df.sort_values(by=['DURACION_HORAS'], ascending=False, inplace=True)
        
        sesiones_sin_asignar = []

        for idx, row in self.df.iterrows():
            asignado = False
            
            grupo_uid = row.get('GRUPO_UID')
            turno_grupo = row['TURNO_GRUPO']
            duracion = int(row['DURACION_HORAS'])
            id_docente = row['ID_DOCENTE']
            
            # Obtenemos rango de horas según el nombre del turno
            bloques_inicio_posibles = self.obtener_bloques_validos(turno_grupo)
            
            # Mezclamos días para no cargar todo al Lunes
            random.shuffle(dias_semana)

            for dia in dias_semana:
                if asignado: break
                
                # Intentar encajar la clase en los bloques disponibles
                for b_inicio in bloques_inicio_posibles:
                    bloques_necesarios = [b_inicio + i for i in range(duracion)]
                    
                    es_posible = True
                    for b in bloques_necesarios:
                        # 1. Validar que la hora existe en el turno (ej: no pasarse de Tarde a Noche si solo es Tarde)
                        if b not in bloques_inicio_posibles: 
                            es_posible = False; break
                        
                        # 2. Validar cruces con BD
                        if self.hay_cruce(id_docente, grupo_uid, dia, b):
                            es_posible = False; break
                    
                    if es_posible:
                        # ¡ÉXITO! Guardamos en el DataFrame en memoria
                        self.df.at[idx, 'DIA'] = dia
                        self.df.at[idx, 'BLOQUE_ORDEN'] = b_inicio
                        
                        # Marcamos ocupado en los sets internos para las siguientes iteraciones
                        for b in bloques_necesarios:
                            self.reservar(id_docente, grupo_uid, dia, b)
                        
                        asignado = True
                        break
            
            if not asignado:
                sesiones_sin_asignar.append(row['ID_SESION'])

        return self.df, sesiones_sin_asignar