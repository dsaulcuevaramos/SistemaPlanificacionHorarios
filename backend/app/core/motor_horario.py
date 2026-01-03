import pandas as pd
import random

class GeneradorHorario:
    def __init__(self, df_sesiones, df_bloques, df_aulas=None):
        """
        df_sesiones: DataFrame con las sesiones pendientes (Export del sistema)
        df_bloques: DataFrame con la configuración de bloques del turno
        df_aulas: DataFrame con aulas disponibles (opcional)
        """
        self.df = df_sesiones.copy()
        self.bloques = df_bloques
        self.aulas = df_aulas if df_aulas is not None else []
        
        # Estructuras de control para colisiones (Memoria del algoritmo)
        # Clave: (NOMBRE_DOCENTE, DIA, BLOQUE) -> True
        self.ocupacion_docente = set()
        # Clave: (NOMBRE_GRUPO, DIA, BLOQUE) -> True
        self.ocupacion_grupo = set()
        
    def obtener_bloques_validos(self, turno_nombre):
        """
        Filtra los bloques permitidos según el turno del grupo.
        Ej: Si es 'Mañana', devuelve bloques 1 al 6.
        """
        # Aquí puedes personalizar tus reglas. 
        # Asumiremos por simplicidad que 'Mañana' son los primeros bloques.
        # En tu sistema real, el ID_TURNO te diría exactamente cuáles son.
        
        todos_los_bloques = self.bloques['orden'].unique()
        todos_los_bloques.sort()
        
        # Simulación simple de reglas de turno (Adaptar a tu lógica real de DB)
        if 'Mañana' in turno_nombre:
            return [b for b in todos_los_bloques if b <= 6] # Bloques 1-6
        elif 'Tarde' in turno_nombre:
            return [b for b in todos_los_bloques if b > 6 and b <= 12]
        elif 'Noche' in turno_nombre:
            return [b for b in todos_los_bloques if b > 12]
        else:
            return todos_los_bloques # Si no especifica, cualquiera sirve

    def hay_cruce(self, docente, grupo, dia, bloque):
        # 1. Validar Docente (Si tiene asignado)
        if docente and docente != "VACANTE":
            if (docente, dia, bloque) in self.ocupacion_docente:
                return True
        
        # 2. Validar Grupo (Alumnos)
        if (grupo, dia, bloque) in self.ocupacion_grupo:
            return True
            
        return False

    def reservar(self, docente, grupo, dia, bloque):
        if docente and docente != "VACANTE":
            self.ocupacion_docente.add((docente, dia, bloque))
        self.ocupacion_grupo.add((grupo, dia, bloque))

    def ejecutar(self):
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        
        # Ordenamos: Primero las sesiones más difíciles (las de práctica o más largas)
        # Esto mejora la probabilidad de encajar todo.
        self.df.sort_values(by=['DURACION_HORAS'], ascending=False, inplace=True)

        sesiones_sin_asignar = []

        for idx, row in self.df.iterrows():
            asignado = False
            
            # Datos de la sesión
            docente = row['DOCENTE']
            grupo = row['GRUPO']
            turno_grupo = row['TURNO_GRUPO']
            
            # Obtener bloques posibles para este grupo
            bloques_posibles = self.obtener_bloques_validos(turno_grupo)
            
            # Intentar asignar (Estrategia Greedy: El primer hueco que encuentre)
            # Para mejor calidad, podrías hacer 'random.shuffle(dias_semana)' para variar
            for dia in dias_semana:
                if asignado: break
                
                for bloque in bloques_posibles:
                    if not self.hay_cruce(docente, grupo, dia, bloque):
                        # ¡Encontramos lugar!
                        
                        # Actualizamos el DataFrame
                        self.df.at[idx, 'DIA'] = dia
                        self.df.at[idx, 'BLOQUE_ORDEN'] = bloque
                        
                        # Reservamos el espacio
                        self.reservar(docente, grupo, dia, bloque)
                        
                        # Opcional: Asignar Aula (Simple Round Robin o Random)
                        if not self.aulas.empty:
                            # Aquí iría lógica compleja de aforo, por ahora asignamos una random disponible
                            aula_random = self.aulas.sample(1).iloc[0]
                            self.df.at[idx, 'ID_AULA'] = aula_random['id']
                        
                        asignado = True
                        break
            
            if not asignado:
                sesiones_sin_asignar.append(row['ID_SESION'])
                print(f"⚠️ No se pudo asignar sesión {row['ID_SESION']} ({row['CURSO']})")

        return self.df, sesiones_sin_asignar