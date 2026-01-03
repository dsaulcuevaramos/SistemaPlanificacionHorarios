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
function getAsignadasPorGrupo(grupoNombre) {
  return horarioAsignado.value.filter(h => h.sesion.grupo.nombre === grupoNombre);
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
function onDragStart(evt, origen, data, asignacionId = null) {
  const payload = {
    origen,
    id_sesion: data.id || data.sesion.id,
    duracion: data.duracion_horas || data.sesion.duracion_horas,
    grupo_nombre: data.grupo?.nombre || data.sesion?.grupo?.nombre,
    asignacionId
  };
  evt.dataTransfer.setData('payload', JSON.stringify(payload));
  evt.dataTransfer.effectAllowed = 'move';
}

async function onDrop(evt, diaNombre, bloqueId, grupoDestinoNombre) {
  const payloadStr = evt.dataTransfer.getData('payload');
  if (!payloadStr) return;
  const item = JSON.parse(payloadStr);

  // Validación de Grupo
  if (item.grupo_nombre !== grupoDestinoNombre) {
    Swal.fire('Acción Bloqueada', `No puedes mezclar grupos (${item.grupo_nombre} -> ${grupoDestinoNombre})`, 'warning');
    return;
  }
  
  // Validación Visual de Espacio (Opcional, el backend valida cruces reales)
  // ... (Tu lógica de Tetris aquí si deseas)

  try { 




    console.log("Enviando Payload:", {
      id_sesion: item.id_sesion,
      id_bloque: bloqueId, // <--- Verifica en la consola que esto NO sea null
      id_periodo: idPeriodo,
      id_aula: null
    });

    if (!bloqueId) {
        throw new Error("El ID del bloque es NULL. Revisa la coincidencia de horas.");
    }




    // Si viene de mover, borramos la anterior
    if (item.origen === 'EXISTING') await horarioService.eliminar(item.asignacionId);

    // Guardar
    await horarioService.asignar({
      id_sesion: item.id_sesion,
      id_bloque: bloqueId, // ID real del bloque (ej: "Lunes 7:00")
      id_periodo: idPeriodo,
      id_aula: null
    });

    await cargarDatos(); // Recargar para ver cambios
    
    // Feedback rápido (Toast)
    const Toast = Swal.mixin({ toast: true, position: 'top-end', showConfirmButton: false, timer: 1500 });
    Toast.fire({ icon: 'success', title: 'Asignado' });

  } catch (error) {
    Swal.fire('Error', error.response?.data?.detail || 'Error al asignar', 'error');
  }
}

async function quitarSesion(idHorario) {
    try {
        await horarioService.eliminar(idHorario);
        await cargarDatos();
    } catch (e) { console.error(e); }
}
</script>

<template>
  <div class="scheduler-layout">
    
    <header class="top-bar">
       <div class="title-area">
          <h2>Gestión de Horarios</h2>
          <small class="text-gray-500">Periodo: {{ props.id_periodo }}</small>
       </div>
       
       <div class="filters-row">
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
             @dragstart="onDragStart($event, 'NEW', sesion)"
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
                        @dragstart="onDragStart($event, 'EXISTING', asig, asig.id)"
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
.content { flex: 1; padding: 2rem; overflow: auto; background-color: #f8fafc; position: relative; }
.loading-overlay { position: absolute; inset: 0; background: rgba(255,255,255,0.8); display: flex; align-items: center; justify-content: center; z-index: 50; font-weight: bold; color: #6366f1; }
.mallas-wrapper { display: flex; gap: 2rem; align-items: flex-start; min-width: min-content; padding-bottom: 40px; }
.empty-main { margin: auto; color: #94a3b8; font-size: 1.2rem; margin-top: 40px; }

/* MALLA CARD */
.malla-card { background: white; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); overflow: hidden; width: 550px; flex-shrink: 0; border: 1px solid #e2e8f0; }
.malla-header { background: #1e293b; color: white; padding: 12px; text-align: center; font-weight: bold; letter-spacing: 0.5px; }

/* GRILLA */
.horario-grid { display: grid; grid-auto-rows: 60px; background: white; position: relative; }
.header-cell { background: #f8fafc; font-weight: 700; text-align: center; padding: 8px; border-bottom: 2px solid #e2e8f0; border-right: 1px solid #f1f5f9; font-size: 0.8rem; color: #475569; display: flex; align-items: center; justify-content: center; grid-row: 1; text-transform: uppercase; }
.time-cell { background: white; font-size: 0.75rem; font-weight: 700; color: #94a3b8; display: flex; align-items: center; justify-content: center; border-right: 2px solid #e2e8f0; border-bottom: 1px dashed #bbcfe2; }
.grid-bg-cell { border-right: 1px solid #f8fafc; border-bottom: 1px solid #f8fafc; z-index: 1; transition: background 0.1s; }
.grid-bg-cell:hover { background: #f0f9ff; }

/* SESIONES ASIGNADAS */
.session-item { z-index: 10; margin: 3px; padding: 6px; border-radius: 6px; font-size: 0.75rem; display: flex; flex-direction: column; justify-content: center; text-align: center; position: relative; cursor: grab; box-shadow: 0 2px 4px rgba(0,0,0,0.05); overflow: hidden; animation: popIn 0.2s ease-out; border: 1px solid rgba(0,0,0,0.05); }
.session-item:active { cursor: grabbing; }
.sess-title { font-weight: 700; line-height: 1.2; margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-box-orient: vertical; }

.teoria { background: #e0e7ff; border-left: 4px solid #4338ca; color: #312e81; }
.practica { background: #d1fae5; border-left: 4px solid #059669; color: #064e3b; }

.btn-remove { position: absolute; top: 2px; right: 2px; background: rgba(255,255,255,0.6); color: #ef4444; border: none; border-radius: 50%; width: 18px; height: 18px; display: none; align-items: center; justify-content: center; cursor: pointer; font-size: 14px; line-height: 1; }
.session-item:hover .btn-remove { display: flex; }
.btn-remove:hover { background: #fee2e2; color: #b91c1c; }

@keyframes popIn { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>