import pandas as pd
import random

class GeneradorHorario:
    def __init__(self, df_sesiones, df_bloques, df_aulas=None, horarios_ocupados=None):
        """
        df_sesiones: Dataframe con las sesiones QUE QUEREMOS PROGRAMAR.
        horarios_ocupados: Lista de diccionarios con lo que YA EXISTE en BD (de otros ciclos).
                           Formato esperado: [{'id_docente': 1, 'dia': 'Lunes', 'id_bloque': 5}, ...]
        """
        self.df = df_sesiones.copy()
        self.bloques = df_bloques
        self.aulas = df_aulas if df_aulas is not None else []
        
        # Estructuras de control para colisiones
        self.ocupacion_docente = set() # (ID_DOCENTE, DIA, ID_BLOQUE)
        self.ocupacion_grupo = set()   # (NOMBRE_GRUPO, DIA, ID_BLOQUE)
        
        # --- NUEVO: PRE-CARGAR LO QUE YA EXISTE EN BD ---
        if horarios_ocupados:
            for h in horarios_ocupados:
                # Bloquear al docente si existe
                if h.get('id_docente'):
                    self.ocupacion_docente.add((h['id_docente'], h['dia'], h['id_bloque']))
                
                # Opcional: Bloquear aulas si gestionas cruces de aula estricto
                # if h.get('id_aula'): ...

    def obtener_bloques_validos(self, turno_nombre):
        # ... (Tu lógica existente se mantiene igual) ...
        # Solo asegúrate de que compare contra 'id_bloque' o 'orden' consistentemente
        todos_los_bloques = self.bloques['orden'].unique()
        todos_los_bloques.sort()
        
        if 'Mañana' in turno_nombre:
            return [b for b in todos_los_bloques if b <= 6] 
        elif 'Tarde' in turno_nombre:
            return [b for b in todos_los_bloques if b > 6 and b <= 12]
        elif 'Noche' in turno_nombre:
            return [b for b in todos_los_bloques if b > 12]
        else:
            return todos_los_bloques

    def hay_cruce(self, id_docente, grupo_nombre, dia, id_bloque):
        # 1. Validar Docente (Usamos ID ahora, es más seguro que nombre)
        if id_docente and id_docente != "VACANTE":
            if (id_docente, dia, id_bloque) in self.ocupacion_docente:
                return True
        
        # 2. Validar Grupo
        if (grupo_nombre, dia, id_bloque) in self.ocupacion_grupo:
            return True
            
        return False

    def reservar(self, id_docente, grupo_nombre, dia, id_bloque):
        if id_docente:
            self.ocupacion_docente.add((id_docente, dia, id_bloque))
        self.ocupacion_grupo.add((grupo_nombre, dia, id_bloque))

    def ejecutar(self):
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        
        # Ordenamos por dificultad (Duración)
        self.df.sort_values(by=['DURACION_HORAS'], ascending=False, inplace=True)
        sesiones_sin_asignar = []

        for idx, row in self.df.iterrows():
            asignado = False
            
            # Datos de la sesión
            id_docente = row['ID_DOCENTE'] # Usaremos ID
            grupo_nombre = row['GRUPO']
            turno_grupo = row['TURNO_GRUPO']
            duracion = int(row['DURACION_HORAS'])
            
            # Bloques validos según turno (Ej: 1, 2, 3...)
            bloques_inicio_posibles = self.obtener_bloques_validos(turno_grupo)
            
            # Mezclar días para variedad
            random.shuffle(dias_semana)

            for dia in dias_semana:
                if asignado: break
                
                for b_inicio in bloques_inicio_posibles:
                    # VERIFICAR CONTIGÜIDAD (Para sesiones de 2 o 3 horas)
                    # Si la clase dura 2 horas, necesitamos que b_inicio y b_inicio+1 estén libres
                    bloques_necesarios = [b_inicio + i for i in range(duracion)]
                    
                    # Verificar si todos los bloques necesarios son válidos y están libres
                    es_posible = True
                    for b in bloques_necesarios:
                        # ¿El bloque existe en el turno? (Evitar saltar de mañana a tarde)
                        if b not in bloques_inicio_posibles: 
                            es_posible = False; break
                        
                        # ¿Hay cruce en ese bloque?
                        if self.hay_cruce(id_docente, grupo_nombre, dia, b):
                            es_posible = False; break
                    
                    if es_posible:
                        # ¡ENCONTRADO! Asignamos todos los bloques
                        for i, b in enumerate(bloques_necesarios):
                            # Si es la primera hora, guardamos en el DF principal
                            # (Nota: Tu estructura actual guarda 1 fila por sesión, 
                            #  así que guardamos el bloque de inicio. El frontend expande la duración).
                            if i == 0:
                                self.df.at[idx, 'DIA'] = dia
                                self.df.at[idx, 'BLOQUE_ORDEN'] = b
                            
                            # Reservamos CADA hora en la memoria del motor
                            self.reservar(id_docente, grupo_nombre, dia, b)
                        
                        asignado = True
                        break
            
            if not asignado:
                sesiones_sin_asignar.append(row['ID_SESION'])

        return self.df, sesiones_sin_asignar