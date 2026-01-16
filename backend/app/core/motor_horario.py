import pandas as pd
import random

class GeneradorHorario:
    def __init__(self, df_sesiones, df_bloques, df_aulas=None, horarios_ocupados=None):
        self.df = df_sesiones.copy()
        self.bloques = df_bloques
        
        # Sets para búsqueda ultrarrápida (O(1))
        self.ocupacion_docente = set() # (ID_DOCENTE, DIA, ID_BLOQUE)
        self.ocupacion_grupo = set()   # (GRUPO_UID, DIA, ID_BLOQUE) <--- AQUÍ ESTÁ LA CLAVE
        
        # --- CARGAR LO QUE YA EXISTE (MANUAL O DE OTROS CICLOS) ---
        if horarios_ocupados:
            for h in horarios_ocupados:
                dia = h['dia']
                bloque = h['id_bloque']

                # 1. Bloquear al Docente (si tiene)
                if h.get('id_docente'):
                    self.ocupacion_docente.add((h['id_docente'], dia, bloque))
                
                # 2. Bloquear al Grupo (¡ESTO ES LO QUE FALTABA!)
                # Si el Grupo A ya tiene clase manual el Lunes a las 7, 
                # lo marcamos como ocupado para que el motor NO ponga nada más ahí.
                if h.get('grupo_uid'):
                    self.ocupacion_grupo.add((str(h['grupo_uid']), dia, bloque))

    def obtener_bloques_validos(self, turno_nombre):
        todos_los_bloques = sorted(self.bloques['orden'].unique())
        if 'Mañana' in turno_nombre:
            return [b for b in todos_los_bloques if b <= 6] 
        elif 'Tarde' in turno_nombre:
            return [b for b in todos_los_bloques if b > 6 and b <= 12]
        elif 'Noche' in turno_nombre:
            return [b for b in todos_los_bloques if b > 12]
        else:
            return todos_los_bloques

    def hay_cruce(self, id_docente, grupo_uid, dia, id_bloque):
        # 1. ¿El Docente está ocupado (manualmente o en otro ciclo)?
        if id_docente and id_docente != "VACANTE":
            if (id_docente, dia, id_bloque) in self.ocupacion_docente:
                return True
        
        # 2. ¿El Grupo está ocupado (manualmente)?
        # Aquí valida: "Si soy el Grupo A (ID 50), ¿tengo algo ya puesto el Lunes a las 7?"
        if (str(grupo_uid), dia, id_bloque) in self.ocupacion_grupo:
            return True
            
        return False

    def reservar(self, id_docente, grupo_uid, dia, id_bloque):
        if id_docente:
            self.ocupacion_docente.add((id_docente, dia, id_bloque))
        self.ocupacion_grupo.add((str(grupo_uid), dia, id_bloque))

    def ejecutar(self):
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        self.df.sort_values(by=['DURACION_HORAS'], ascending=False, inplace=True)
        sesiones_sin_asignar = []

        for idx, row in self.df.iterrows():
            asignado = False
            
            grupo_uid = row.get('GRUPO_UID') # ID único de la BD
            turno_grupo = row['TURNO_GRUPO']
            duracion = int(row['DURACION_HORAS'])
            id_docente = row['ID_DOCENTE']
            
            bloques_inicio_posibles = self.obtener_bloques_validos(turno_grupo)
            random.shuffle(dias_semana)

            for dia in dias_semana:
                if asignado: break
                
                for b_inicio in bloques_inicio_posibles:
                    bloques_necesarios = [b_inicio + i for i in range(duracion)]
                    
                    es_posible = True
                    for b in bloques_necesarios:
                        # Validar límites de turno y CRUCES (Manuales incluidos)
                        if b not in bloques_inicio_posibles: 
                            es_posible = False; break
                        
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