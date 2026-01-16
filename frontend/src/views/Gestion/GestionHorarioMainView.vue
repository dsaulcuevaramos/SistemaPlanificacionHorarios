<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import horarioService from '../../api/horarioService';
import turnoService from '../../api/turnoService';
import periodoService from '../../api/periodoService';
import Swal from 'sweetalert2';

const props = defineProps(['id_periodo']);
const idPeriodo = parseInt(props.id_periodo);

// --- ESTADO ---
const ciclosDisponibles = ref([]);
const cicloSeleccionado = ref(null);
const turnosDisponibles = ref([]);
const idTurnoSeleccionado = ref(null);

const bloques = ref([]);           // Todos los bloques del turno (filas repetidas por día)
const sesionesPendientes = ref([]); // Data cruda de sesiones
const horarioAsignado = ref([]);    // Data cruda de asignaciones

const loading = ref(false);



// --- INICIO ---
onMounted(async () => {
  loading.value = true;
  try {
    // 1. Cargar Ciclos (Filtrados por paridad desde el Back)
    try {
        // A. Traemos el periodo completo para ver su descripción
        const periodoObj = await periodoService.getById(idPeriodo);
        
        // B. Detectamos la paridad
        // Buscamos si la descripción dice "PAR" (y no "IMPAR") o si el código termina en II
        // Ajusta la palabra clave según lo que guardes en tu BD: "Semestre Par", "2025-II", etc.
        const descripcion = (periodoObj.descripcion || '').toUpperCase();
        const codigo = (periodoObj.codigo || '').toUpperCase();
        
        // Lógica: Es par si la descripción tiene 'PAR' (cuidado con imPAR) o código tiene 'II'
        // Una forma segura: Si dice "IMPAR" es impar, sino si dice "PAR" es par.
        let esPar = false;

        if (descripcion.includes('IMPAR') || codigo.endsWith('I') && !codigo.endsWith('II')) {
            esPar = false;
        } else if (descripcion.includes('PAR') || codigo.endsWith('II') || codigo.endsWith('2')) {
            esPar = true;
        }

        // C. Generamos los ciclos
        if (esPar) {
            ciclosDisponibles.value = [2, 4, 6, 8, 10];
        } else {
            ciclosDisponibles.value = [1, 3, 5, 7, 9];
        }

        // D. Seleccionar el primero por defecto
        if (ciclosDisponibles.value.length > 0) {
            cicloSeleccionado.value = ciclosDisponibles.value[0];
        }

    } catch (e) {
        console.warn("No se pudo detectar paridad del periodo, mostrando todos los ciclos.", e);
        // Fallback seguro: Mostrar TODOS para no bloquearte
        ciclosDisponibles.value = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
        cicloSeleccionado.value = 1;
    }

    // 2. Cargar Turnos
    turnosDisponibles.value = await turnoService.getAll();
    if (turnosDisponibles.value.length > 0) {
        idTurnoSeleccionado.value = turnosDisponibles.value[0].id;
    }

    // 3. Cargar Datos Globales
    await cargarDatos();

  } catch (error) {
    console.error(error);
    Swal.fire('Error', 'No se pudieron cargar los datos iniciales.', 'error');
  } finally {
    loading.value = false;
  }
});

// Recargar al cambiar turno (porque cambian los bloques y los pendientes)
watch(idTurnoSeleccionado, async (val) => {
    if (val) await cargarDatos();
});


const horariosFiltradosPorVista = computed(() => {
  if (!cicloSeleccionado.value) return [];
  
  return horarioAsignado.value.filter(h => {
    // Valida que el curso pertenezca al ciclo actual
    const cicloCurso = h.sesion?.grupo?.curso_aperturado?.curso?.ciclo;
    return cicloCurso === cicloSeleccionado.value;
  });
});

async function cargarDatos() {
  loading.value = true;
  try {
    // A. Cargar Bloques del Turno actual (Define la forma de la grilla)
    if (idTurnoSeleccionado.value) {
        bloques.value = await horarioService.getBloquesByTurno(idTurnoSeleccionado.value);
    }

    // B. Cargar Sesiones y Asignaciones
    const [sesionesResp, horarioResp] = await Promise.all([
        horarioService.getSesionesPendientes(idPeriodo),
        horarioService.getHorarioCompleto(idPeriodo)
    ]);
    sesionesPendientes.value = sesionesResp;
    horarioAsignado.value = horarioResp;

  } catch (e) {
    console.error("Error cargando datos:", e);
  } finally {
    loading.value = false;
  }
}


// --- COMPUTED: LÓGICA DE LA GRILLA DINÁMICA ---

// 1. DÍAS DINÁMICOS (Columnas)
// Analiza los bloques cargados y saca los días únicos ordenados.
// Ej: Si el turno Noche solo tiene bloques L-M-X, solo devuelve esos 3 días.
const diasDinamicos = computed(() => {
    if (bloques.value.length === 0) return ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];
    
    const ordenDias = { 'Lunes': 1, 'Martes': 2, 'Miércoles': 3, 'Jueves': 4, 'Viernes': 5, 'Sábado': 6, 'Domingo': 7 };
    const unicos = new Set(bloques.value.map(b => b.dia_semana));
    return Array.from(unicos).sort((a, b) => ordenDias[a] - ordenDias[b]);
});

// 2. HORAS ÚNICAS (Filas)
// Extrae las horas de inicio únicas para dibujar la columna izquierda.
const filasHoras = computed(() => {
    if (bloques.value.length === 0) return [];
    const map = new Map();
    bloques.value.forEach(b => {
        if (!map.has(b.hora_inicio)) map.set(b.hora_inicio, b);
    });
    // Ordenamos por el campo 'orden' que viene de BD
    return Array.from(map.values()).sort((a, b) => a.orden - b.orden);
});

// 3. FILTRO DE PENDIENTES
// Muestra solo sesiones que coincidan con Ciclo Y Turno seleccionados
const pendientesFiltrados = computed(() => {

  const conteoHoras = {};
  
  if (horarioAsignado.value) {
      horarioAsignado.value.forEach(h => {
        // Usamos '?.' para evitar errores si viene data corrupta
        const idSesion = h.sesion?.id; 
        if (idSesion) {
            conteoHoras[idSesion] = (conteoHoras[idSesion] || 0) + 1;
        }
      });
  }

  return sesionesPendientes.value.filter(s => {
    // A. Validaciones de seguridad (evitar undefined)
    if (!s.grupo) return false;

    // B. Filtros de UI (Ciclo y Turno)
    const matchCicloTurno = 
        s.grupo?.curso_aperturado?.curso?.ciclo === cicloSeleccionado.value &&
        s.grupo?.id_turno === idTurnoSeleccionado.value;

    // C. VALIDACIÓN CLAVE: ¿Está completa?
    // Verificamos si las horas asignadas en la grilla son menores a la duración total
    const horasAsignadas = conteoHoras[s.id] || 0;
    const estaPendiente = horasAsignadas < s.duracion_horas;

    return matchCicloTurno && estaPendiente;
  });
});

// 4. DETECTOR DE GRUPOS (Mallas)
// Decide cuántas mallas dibujar (A, B, C...) basándose en el Ciclo y Turno activos.
const gruposDelCiclo = computed(() => {
  if (!cicloSeleccionado.value || !idTurnoSeleccionado.value) return [];

  // Función filtro BLINDADA
  const filtro = (item) => {
      // 1. Si el item no existe, falso
      if (!item) return false;
      
      // 2. Si el item no tiene grupo (esto causaba tu error), falso
      if (!item.grupo) return false;

      // 3. Comparación segura usando '?.'
      return item.grupo?.curso_aperturado?.curso?.ciclo === cicloSeleccionado.value && 
            item.grupo?.id_turno === idTurnoSeleccionado.value;
  };

  // Filtrar pendientes
  const enPendientes = sesionesPendientes.value
    .filter(s => filtro(s))
    .map(s => s.grupo?.nombre);

  // Filtrar asignados (Aquí es donde fallaba porque h.sesion era undefined)
  const enAsignados = horarioAsignado.value
    .filter(h => h.sesion && filtro(h.sesion)) // Verificamos h.sesion antes de pasarlo
    .map(h => h.sesion?.grupo?.nombre);

  // Unir y limpiar
  const unicos = new Set([...enPendientes, ...enAsignados].filter(n => n)); // Filtra nulos
  return Array.from(unicos).sort(); 
});





// --- HELPERS ---
const mapaOcupacion = computed(() => {
    const mapa = {}; // Clave: "idSesion-dia-orden" -> Boolean
    horarioAsignado.value.forEach(h => {
        // Aseguramos leer la estructura anidada correctamente
        if (h.sesion && h.bloque_horario) {
            const key = `${h.sesion.id}-${h.bloque_horario.dia_semana}-${h.bloque_horario.orden}`;
            mapa[key] = true;
        }
    });
    return mapa;
});

// 2. Función corregida: Solo devuelve la "Cabeza" de la sesión
function getAsignadasPorGrupo(grupoNombre) {
    return horarioAsignado.value.filter(h => {
        // --- 1. SEGURIDAD DE DATOS ---
        if (!h.sesion?.grupo?.curso_aperturado?.curso) return false;
        if (!h.bloque_horario) return false;

        // --- 2. FILTROS LÓGICOS (LO QUE FALLABA) ---
        
        // A. ¿Es del grupo correcto? (Ej: "A")
        const matchGrupo = h.sesion.grupo.nombre === grupoNombre;
        
        // B. ¿Es del CICLO seleccionado? (¡CRÍTICO!)
        const matchCiclo = h.sesion.grupo.curso_aperturado.curso.ciclo === cicloSeleccionado.value;
        
        // C. ¿Es del TURNO seleccionado?
        const matchTurno = h.sesion.grupo.id_turno === idTurnoSeleccionado.value;

        // Si falla cualquiera de estos, NO pertenece a esta pantalla.
        if (!matchGrupo || !matchCiclo || !matchTurno) return false;

        // --- 3. FILTRO VISUAL (SPAN) ---
        
        // Datos actuales
        const ordenActual = h.bloque_horario.orden;
        const dia = h.bloque_horario.dia_semana;
        const idSesion = h.sesion.id;

        // Buscamos si existe el bloque "anterior" (orden - 1)
        const keyAnterior = `${idSesion}-${dia}-${ordenActual - 1}`;
        
        // Si existe el anterior, significa que yo soy la "cola" de una clase larga.
        // NO me dibujes, porque mi hermano mayor (la cabeza) ya ocupó el espacio con 'span'.
        if (mapaOcupacion.value[keyAnterior]) {
            return false; 
        }

        // Si pasé todos los filtros: Soy del ciclo correcto, del grupo correcto y soy la cabeza.
        return true;
    });
}






// Obtiene el ID exacto del bloque DB para una combinación Dia + Hora
function getBloqueId(dia, horaInicio) {
    // Aseguramos que horaInicio sea string
    const horaBusqueda = String(horaInicio).substring(0, 5); 

    const bloque = bloques.value.find(bk => {
        // Comparamos también cortando los segundos del bloque en memoria
        const horaBloque = String(bk.hora_inicio).substring(0, 5);
        return bk.dia_semana === dia && horaBloque === horaBusqueda;
    });

    return bloque ? bloque.id : null;
}

// Calcula la fila CSS basada en el índice de la hora
function getFilaIndex(horaInicio) {
    return filasHoras.value.findIndex(f => f.hora_inicio === horaInicio);
}

// --- DRAG & DROP ---
function onDragStart(evt, origen, sesionData, asignacionId = null, nombreGrupoExplicit = null) {
  const payload = {
    origen,
    id_sesion: sesionData.id,
    duracion: sesionData.duracion_horas,
    
    // AQUÍ EL CAMBIO: Si me dan el nombre explícito, lo uso. Si no, trato de leerlo del objeto.
    grupo_nombre: nombreGrupoExplicit || sesionData.grupo?.nombre,
    
    asignacionId
  };
  evt.dataTransfer.setData('payload', JSON.stringify(payload));
  evt.dataTransfer.effectAllowed = 'move';
}

async function onDrop(evt, diaNombre, bloqueId, grupoDestinoNombre) {
  const payloadStr = evt.dataTransfer.getData('payload');
  if (!payloadStr) return;
  const item = JSON.parse(payloadStr);

  // Validación 1: No mezclar grupos
  if (item.grupo_nombre !== grupoDestinoNombre) {
    Swal.fire('Acción Bloqueada', `No puedes mover del Grupo ${item.grupo_nombre} al ${grupoDestinoNombre}`, 'warning');
    return;
  }

  // Validación 2: Evitar soltar en el mismo lugar (si es movimiento)
  // (Opcional, pero ahorra una llamada a la API)
  
  try {
    // === PASO CLAVE PARA MOVER ===
    // Si la ficha viene de la grilla ('EXISTING'), primero la eliminamos de su lugar anterior.
    // Usamos 'await' para asegurar que se borre ANTES de intentar asignar la nueva.
    if (item.origen === 'EXISTING' && item.asignacionId) {
        await horarioService.eliminar(item.asignacionId);
    }

    // === PASO DE ASIGNACIÓN ===
    // Ahora que el espacio (o el docente) se liberó, creamos la nueva asignación
    await horarioService.asignar({
      id_sesion: item.id_sesion,
      id_bloque: bloqueId,
      id_periodo: idPeriodo,
      id_aula: null
    });

    // Recargar todo para ver el cambio
    await cargarDatos(); 
    
    // Feedback suave (Toast)
    const Toast = Swal.mixin({ toast: true, position: 'top-end', showConfirmButton: false, timer: 1500 });
    Toast.fire({ icon: 'success', title: item.origen === 'EXISTING' ? 'Reubicado' : 'Asignado' });

  } catch (error) {
    console.error(error);
    
    // CASO DE ERROR AL MOVER:
    // Si falló la nueva asignación (ej: cruce) pero ya borramos la anterior,
    // el curso se iría a "Pendientes". 
    // Podrías intentar restaurarlo, pero recargando datos aparecerá en la barra lateral.
    
    let msg = error.response?.data?.detail || 'No se pudo asignar el horario';
    
    // Si es un error de cruce conocido (Error 400 del backend)
    if (msg.includes('Cruce') || msg.includes('ocupado')) {
         Swal.fire('Ocupado', msg, 'warning');
    } else {
         Swal.fire('Error', msg, 'error');
    }
    
    // Siempre recargar por si acaso quedó un estado inconsistente visual
    await cargarDatos(); 
  }
}

async function quitarSesion(idHorario) {
    try {
        await horarioService.eliminar(idHorario);
        await cargarDatos();
    } catch (e) { console.error(e); }
}



const autogenerar = async () => {
  if (!cicloSeleccionado.value) return Swal.fire('Error', 'Selecciona un ciclo primero', 'warning');

  const confirm = await Swal.fire({
    title: `¿Autogenerar Ciclo ${cicloSeleccionado.value}?`,
    text: "Se programarán las sesiones pendientes respetando los horarios ya existentes.",
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Sí, generar'
  });

  if (confirm.isConfirmed) {
    try {
       loading.value = true;
       const res = await horarioService.autogenerarCiclo(idPeriodo, cicloSeleccionado.value);

       await cargarDatos(); // Recargar la malla

       Swal.fire('Proceso Terminado', `Generados: ${res.data.generados}. No asignados: ${res.data.fallos}`, 'success');
    } catch (e) {
       Swal.fire('Error', 'Falló la generación automática', 'error');
    } finally {
       loading.value = false;
    }
  }
};





const descargarExcel = async () => {
    try {
        Swal.fire({
            title: 'Generando Reporte...',
            text: 'Preparando formato institucional...',
            allowOutsideClick: false,
            didOpen: () => Swal.showLoading()
        });

        const response = await horarioService.descargarReporteExcel(idPeriodo);

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `Horario_General_P${idPeriodo}.xlsx`);
        document.body.appendChild(link);
        link.click();
        
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        Swal.close();
        
        const Toast = Swal.mixin({ toast: true, position: 'top-end', showConfirmButton: false, timer: 3000 });
        Toast.fire({ icon: 'success', title: 'Descarga exitosa' });

    } catch (e) {
        console.error(e);
        const msg = e.response?.data?.detail || 'No se pudo generar el reporte.';
        Swal.fire('Error', msg, 'error');
    }
};

</script>

<template>
  <div class="scheduler-layout">
    
    <header class="top-bar">
       <div class="title-area">
          <h2>Gestión de Horarios</h2>
          <small class="text-gray-500">Periodo: {{ props.id_periodo }}</small>
       </div>
       
       <div class="filters-row">


          
            <button @click="descargarExcel" class="btn-excel" title="Descargar Reporte General">
                <i class="fas fa-file-excel"></i> Exportar
            </button>
   

            <button 
                v-if="pendientesFiltrados.length > 0"
                @click="autogenerar" 
                class="btn-generate-mini"
                title="Autocompletar pendientes de este ciclo"
            >
                ⚡ Autogenerar
            </button>


           <div class="control-group">
              <label>Ciclo:</label>
              <select v-model="cicloSeleccionado" class="form-select">
                 <option v-for="c in ciclosDisponibles" :key="c" :value="c">Ciclo {{ c }}</option>
              </select>
           </div>

           <div class="control-group">
              <label>Turno:</label>
              <select v-model="idTurnoSeleccionado" class="form-select">
                 <option v-for="t in turnosDisponibles" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
           </div>
       </div>
    </header>

    <div class="workspace">
       <aside class="sidebar">
          <h3>Pendientes</h3>
          <div class="sub-info">
             Ciclo {{ cicloSeleccionado }} • {{ turnosDisponibles.find(t=>t.id===idTurnoSeleccionado)?.nombre }}
          </div>

          <div v-if="pendientesFiltrados.length === 0" class="empty-state">
             ✅ Todo asignado
          </div>
          
          <div 
             v-for="sesion in pendientesFiltrados" 
             :key="sesion.id"
             class="ficha-sidebar"
             :class="sesion.grupo.nombre === 'A' ? 'border-indigo' : 'border-pink'"
             draggable="true"
             @dragstart="onDragStart($event, 'NEW', sesion, null, sesion.grupo.nombre)"
          >
              <div class="ficha-header">
                  <span class="badge">{{ sesion.grupo.nombre }}</span>
                  <span class="duracion">{{ sesion.duracion_horas }}h</span>
              </div>
              <strong>{{ sesion.grupo?.curso_aperturado?.curso?.nombre || 'Curso Desconocido' }}</strong>
              <div class="docente">{{ sesion.grupo?.docente?.apellido || 'VACANTE' }}</div>
          </div>
       </aside>

       <main class="content">
          <div v-if="loading" class="loading-overlay">Cargando...</div>
          
          <div class="mallas-wrapper">
             <div v-if="!loading && gruposDelCiclo.length === 0" class="empty-main">
                No hay grupos registrados para este Ciclo y Turno.
             </div>

             <div v-for="grupoNombre in gruposDelCiclo" :key="grupoNombre" class="malla-card">
                <div class="malla-header">GRUPO {{ grupoNombre }}</div>
                
                <div class="horario-grid" 
                     :style="{ gridTemplateColumns: `70px repeat(${diasDinamicos.length}, 1fr)` }">
                   
                   <div class="header-cell corner">HORA</div>
                   <div v-for="dia in diasDinamicos" :key="dia" class="header-cell">{{ dia }}</div>

                   <div v-for="(fHora, idx) in filasHoras" :key="'row-'+idx" 
                        class="time-cell" :style="{ gridColumn: 1, gridRow: idx + 2 }">
                        {{ fHora.hora_inicio.substring(0,5) }}
                   </div>

                   <template v-for="(fHora, fIdx) in filasHoras" :key="'bg-'+fIdx">
                      <div v-for="(dia, dIdx) in diasDinamicos" :key="dia+'-'+fIdx"
                           class="grid-bg-cell"
                           :style="{ gridColumn: dIdx + 2, gridRow: fIdx + 2 }"
                           @dragover.prevent
                           @drop="onDrop($event, dia, getBloqueId(dia, fHora.hora_inicio), grupoNombre)"
                      ></div>
                   </template>

                   <div v-for="asig in getAsignadasPorGrupo(grupoNombre)" :key="asig.id"
                        class="session-item"
                        :class="asig.sesion.tipo_sesion === 'TEORIA' ? 'teoria' : 'practica'"
                        draggable="true"
                        @dragstart="onDragStart($event, 'EXISTING', asig.sesion, asig.id, grupoNombre)"
                        :style="{
                           gridColumn: diasDinamicos.indexOf(asig.bloque_horario.dia_semana) + 2,
                           gridRow: `${getFilaIndex(asig.bloque_horario.hora_inicio) + 2} / span ${asig.sesion.duracion_horas}`
                        }"
                   >
                      <button class="btn-remove" @click.stop="quitarSesion(asig.id)">×</button>
                      <div class="sess-title">{{ asig.sesion.grupo.curso_aperturado.curso.nombre }}</div>
                      <small>{{ asig.sesion.grupo.docente?.apellido || 'VACANTE' }}</small>
                   </div>

                </div>
             </div>

          </div>
       </main>
    </div>
  </div>
</template>

<style scoped>
/* ESTRUCTURA GENERAL */
.scheduler-layout { display: flex; flex-direction: column; height: 100vh; background: #f1f5f9; font-family: 'Segoe UI', sans-serif; }

/* HEADER */
.top-bar { background: white; padding: 10px 24px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 2px rgba(0,0,0,0.05); z-index: 20; }
.filters-row { display: flex; gap: 24px; }
.control-group { display: flex; align-items: center; gap: 8px; }
.control-group label { font-weight: 600; color: #475569; font-size: 0.9rem; }
.form-select { padding: 6px 12px; border: 1px solid #cbd5e1; border-radius: 6px; background-color: white; font-size: 0.9rem; min-width: 140px; cursor: pointer; }
.form-select:focus { outline: none; border-color: #6366f1}

/* WORKSPACE */
.workspace { display: flex; flex: 1; overflow: hidden; }

/* SIDEBAR */
.sidebar { width: 280px; background: white; padding: 1.5rem; border-right: 1px solid #e2e8f0; overflow-y: auto; display: flex; flex-direction: column; }
.sidebar h3 { margin: 0 0 5px 0; font-size: 1.1rem; color: #1e293b; }
.sub-info { font-size: 0.8rem; color: #64748b; margin-bottom: 1.5rem; }
.empty-state { text-align: center; color: #94a3b8; padding: 20px; font-style: italic; background: #f8fafc; border-radius: 8px; }

/* FICHAS SIDEBAR */
.ficha-sidebar { background: white; color: #1a2233; border: 1px solid #e2e8f0; padding: 12px; margin-bottom: 12px; cursor: grab; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border-left-width: 4px; transition: transform 0.1s, box-shadow 0.1s; }
.ficha-sidebar:hover { transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }

.ficha-sidebar:active { cursor: grabbing; }
.ficha-header { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 0.75rem; }
.badge { background: #f1f5f9; color: #475569; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
.duracion { font-family: monospace; color: #64748b; font-weight: 600; }
.docente { font-size: 0.8rem; color: #64748b; margin-top: 4px; }
.border-indigo { border-left-color: #6366f1; }
.border-pink { border-left-color: #ec4899; }

/* CONTENIDO PRINCIPAL */
.content { 
    flex: 1; 
    padding: 2rem; 
    overflow: hidden; /* Ocultamos el scroll global */
    background-color: #f8fafc; 
    position: relative; 
    display: flex;
    flex-direction: column;
}

.loading-overlay { position: absolute; inset: 0; background: rgba(255,255,255,0.8); display: flex; align-items: center; justify-content: center; z-index: 50; font-weight: bold; color: #6366f1; }
.mallas-wrapper { 
    display: flex; 
    gap: 2rem; 
    align-items: flex-start; 
    
    /* --- CORRECCIÓN DE SCROLL --- */
    overflow-x: auto;       /* Scroll horizontal activado */
    overflow-y: hidden;     /* Sin scroll vertical en este eje */
    padding-bottom: 20px;   /* Espacio para la barra */
    width: 100%;            
    height: 100%;           /* Ocupar toda la altura */
}

.empty-main { margin: auto; color: #94a3b8; font-size: 1.2rem; margin-top: 40px; }

/* MALLA CARD */
.malla-card { 
    background: white; 
    border-radius: 12px; 
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); 
    overflow: visible;      /* Permitir ver sombras */
    border: 1px solid #e2e8f0;
    
    /* --- CORRECCIÓN DE TAMAÑO --- */
    flex: 0 0 550px;        /* ¡NO ENCOGER! Ancho fijo de 550px */
    width: 550px;           
}
.malla-header { background: #1e293b; color: white; padding: 12px; text-align: center; font-weight: bold; letter-spacing: 0.5px; }

/* GRILLA */
.horario-grid { display: grid; grid-auto-rows: 60px; background: white; position: relative; }
.header-cell { background: #f8fafc; font-weight: 700; text-align: center; padding: 8px; border-bottom: 2px solid #e2e8f0; border-right: 1px solid #f1f5f9; font-size: 0.8rem; color: #475569; display: flex; align-items: center; justify-content: center; grid-row: 1; text-transform: uppercase; }
.time-cell { background: white; font-size: 0.75rem; font-weight: 700; color: #94a3b8; display: flex; align-items: center; justify-content: center; border-right: 2px solid #e2e8f0; border-bottom: 1px dashed #bbcfe2; }
.grid-bg-cell { border-right: 1px solid #f8fafc; border-bottom: 1px solid #f8fafc; z-index: 1; transition: background 0.1s; }
.grid-bg-cell:hover { background: #f0f9ff; }

/* SESIONES ASIGNADAS */
.session-item { 
    z-index: 10; 
    margin: 1px; /* Pequeño margen para ver si hay algo detrás */
    padding: 6px; 
    border-radius: 6px; 
    font-size: 0.75rem; 
    display: flex; 
    flex-direction: column; 
    justify-content: center; 
    text-align: center; 
    position: relative; 
    cursor: grab; 
    box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* Sombra más fuerte para notar superposición */
    overflow: visible;
    border: 1px solid rgba(0,0,0,0.1); 
    
    /* ASEGURAR FONDO OPACO */
    opacity: 1 !important; 
}
.session-item:active { cursor: grabbing; }
.sess-title { font-weight: 700; line-height: 1.2; margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-box-orient: vertical; }

.teoria { background: #e0e7ff; border-left: 4px solid #4338ca; color: #312e81; }
.practica { background: #d1fae5; border-left: 4px solid #059669; color: #064e3b; }

.btn-remove { 
    position: absolute; 
    top: -8px;       /* Lo sacamos un poco hacia arriba para que no tape texto */
    right: -8px;     /* Lo sacamos a la derecha */
    
    background: #ef4444; /* Rojo sólido */
    color: white;        /* X blanca */
    
    border: 2px solid white; /* Borde blanco para separar del curso */
    border-radius: 50%; 
    
    width: 26px;     /* Mucho más grande (antes 18px) */
    height: 26px; 
    
    display: none;   /* Se oculta por defecto */
    align-items: center; 
    justify-content: center; 
    cursor: pointer; 
    font-size: 16px; 
    font-weight: bold;
    z-index: 50;     /* Asegura que esté encima de todo */
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    transition: transform 0.1s;
}
.btn-remove:hover { 
    background: #dc2626; 
    transform: scale(1.1);
}

.session-item:hover .btn-remove { display: flex; }
.btn-remove:hover { background: #fee2e2; color: #b91c1c; }


.btn-generate-mini {
  background: #8b5cf6; color: white; border: none; padding: 0 16px; 
  border-radius: 6px; font-weight: 700; cursor: pointer;
  display: flex; align-items: center; gap: 5px;
  transition: transform 0.1s;
}
.btn-generate-mini:active { transform: scale(0.95); }

.btn-excel {
    display: flex;
    align-items: center;
    gap: 8px;
    background-color: #107c41; /* Verde Excel */
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
    height: 38px; /* Para igualar altura de selects */
}

.btn-excel:hover {
    background-color: #0c5e31;
}

.btn-excel i {
    font-size: 1.1rem;
}

@keyframes popIn { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>