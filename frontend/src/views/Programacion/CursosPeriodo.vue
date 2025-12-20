<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Swal from 'sweetalert2';
import { useAuthStore } from '../../stores/authStore'; // 1. Importamos AuthStore

// Servicios API
import periodoService from '../../api/periodoService';
import planService from '../../api/planEstudioService';
import cursoService from '../../api/cursoService';
import api from '../../api/axios';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore(); // 2. Instancia del store
const idPeriodo = route.params.id;

// --- ESTADO ---
const periodo = ref(null);
const planes = ref([]);
const planVersiones = ref([]);

// "allCursos" tendrá TODOS los cursos de la escuela (cache)
// "cursos" tendrá solo los filtrados por la versión (para la tabla)
const allCursos = ref([]); 
const cursos = ref([]); 

// Selecciones
const selectedPlan = ref(null);
const selectedVersion = ref(null);
const cuposGeneral = ref(40);
const selectedIds = ref([]); // Checkboxes

const loading = ref(false);
const saving = ref(false);
const savedInDbIds = ref([]);

// --- CARGA INICIAL ---
const initData = async () => {
  loading.value = true;
  try {
    const [periodoResp, planesResp, cursosResp] = await Promise.all([
        periodoService.getById(idPeriodo), 
        planService.getAllPlanes(),        // 2. Planes
        cursoService.getAll()              // 3. Cursos
    ]);

    // Asignaciones
    periodo.value = periodoResp;
    planes.value = planesResp || [];
    allCursos.value = cursosResp || []; 

    if (planes.value.length > 0) {
        const planesOrdenados = [...planes.value].sort((a, b) => b.id - a.id);
        selectedPlan.value = planesOrdenados[0].id;
    }

    // Cargar aperturas guardadas
    await cargarAperturasExistentes();

  } catch (error) {
    console.error("Error initData:", error);
    Swal.fire('Error', 'No se pudieron cargar los datos.', 'error');
  } finally {
    loading.value = false;
  }
};

const cursosRegistrados = computed(() => {
    return allCursos.value.filter(c => savedInDbIds.value.includes(c.id))
                         .sort((a, b) => a.ciclo - b.ciclo);
});

const cargarAperturasExistentes = async () => {
    try {
        const { data } = await api.get(`/aperturas/${idPeriodo}`);
        savedInDbIds.value = data.map(a => a.id_curso); 
        // Inicializamos los seleccionados con lo que ya existe
        selectedIds.value = [...savedInDbIds.value];
    } catch (e) {
        console.error("Error cargando aperturas:", e);
    }
};


const limpiarSeleccionNoGuardada = () => {
    // Volvemos el estado de los checks a lo que hay en la base de datos
    selectedIds.value = [...savedInDbIds.value];
    
    const Toast = Swal.mixin({ toast: true, position: 'top-end', showConfirmButton: false, timer: 2000 });
    Toast.fire({ icon: 'info', title: 'Selección temporal limpiada' });
};


onMounted(() => initData());

// --- CASCADA 1: PLAN -> VERSIONES (Lógica traída del Catálogo) ---
watch(selectedPlan, async (newPlanId) => {
    // Limpieza
    selectedVersion.value = null;
    planVersiones.value = [];
    cursos.value = []; // Limpiamos la tabla visual
    
    if (!newPlanId) return;

    loading.value = true;
    try {
        const data = await planService.getAllVersionesByPlan(newPlanId);
        
        // Filtro de seguridad (Igual que en tu Catálogo)
        const versiones = data.filter(v => v.id_plan === newPlanId || v.id_plan_estudio === newPlanId);
        
        // Ordenar descendente
        planVersiones.value = versiones.sort((a, b) => b.id - a.id);

        // Auto-seleccionar última versión
        if (planVersiones.value.length > 0) {
            selectedVersion.value = planVersiones.value[0].id;
        }
    } catch (error) {
        console.error(error);
        Swal.fire('Error', 'Error al cargar versiones del plan', 'error');
    } finally {
        loading.value = false;
    }
});

// --- CASCADA 2: VERSIÓN -> FILTRADO DE CURSOS ---
watch(selectedVersion, (newVersionId) => {
    if (!newVersionId) {
        cursos.value = [];
        return;
    }

    // AQUI ESTA LA CLAVE: No llamamos a la API, filtramos lo que ya cargamos en initData
    // Esto asegura que usamos la misma data que el catálogo
    const cursosFiltrados = allCursos.value.filter(c => c.id_plan_version === newVersionId);
    
    // Ordenamos por ciclo para visualización
    cursos.value = cursosFiltrados.sort((a, b) => a.ciclo - b.ciclo);

    // Aplicar lógica de pre-selección (Paridad)
    aplicarLogicaParidad();
});

const aplicarLogicaParidad = () => {
    if (!periodo.value || cursos.value.length === 0) return;

    const codigoPeriodo = periodo.value.codigo.toUpperCase();
    const esPar = codigoPeriodo.includes('II') || codigoPeriodo.includes('PAR');
    const esImpar = !esPar; 

    const nuevosSeleccionados = [];

    cursos.value.forEach(curso => {
        // Solo pre-seleccionamos si NO está desactivado (estado 1)
        if (curso.estado === 0) return; 

        let debeSeleccionarse = false;

        if (curso.paridad === 'AMBOS') debeSeleccionarse = true;
        else if (curso.paridad === 'PAR' && esPar) debeSeleccionarse = true;
        else if (curso.paridad === 'IMPAR' && esImpar) debeSeleccionarse = true;
        else if (curso.ciclo) {
            const cicloEsPar = curso.ciclo % 2 === 0;
            if (esPar && cicloEsPar) debeSeleccionarse = true;
            if (esImpar && !cicloEsPar) debeSeleccionarse = true;
        }

        if (debeSeleccionarse) {
            nuevosSeleccionados.push(curso.id);
        }
    });

    // Mantenemos lo que ya estaba seleccionado (de BD) y agregamos lo nuevo
    const seleccionFinal = new Set([...selectedIds.value, ...nuevosSeleccionados]);
    selectedIds.value = Array.from(seleccionFinal);
};

// --- GUARDAR ---
const guardarProgramacion = async () => {
    if (selectedIds.value.length === 0) {
        Swal.fire('Atención', 'No has seleccionado ningún curso.', 'warning');
        return;
    }

    const result = await Swal.fire({
        title: '¿Confirmar Apertura?',
        text: `Se programarán ${selectedIds.value.length} cursos.`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Sí, guardar',
        confirmButtonColor: '#4f46e5'
    });

    if (!result.isConfirmed) return;

    saving.value = true;
    try {
        const payload = {
            id_periodo: parseInt(idPeriodo),
            ids_cursos: selectedIds.value,
            cupos_general: cuposGeneral.value
        };

        // CAMBIO: Ahora apuntamos a la nueva ruta /aperturas/masiva
        await api.post('/aperturas/masiva', payload); 

        Swal.fire('¡Éxito!', 'La programación se ha guardado.', 'success');
    } catch (error) {
        console.error(error);
        Swal.fire('Error', 'No se pudo guardar la programación.', 'error');
    } finally {
        saving.value = false;
    }
};

const volver = () => router.push(`/programacion/periodo/${idPeriodo}`);

const toggleSelection = (id) => {
    const index = selectedIds.value.indexOf(id);
    if (index === -1) selectedIds.value.push(id);
    else selectedIds.value.splice(index, 1);
};

const periodoInfo = computed(() => periodo.value ? `${periodo.value.codigo}` : '...');

</script>

<template>
  <div class="page-content">
    
    <div class="view-header">
      <div class="flex items-center gap-4">
        <button @click="volver" class="btn-back">← Volver</button>
        <div>
          <h1 class="title">Programación Académica</h1>
          <p class="subtitle">Periodo: <span class="text-indigo-600 font-bold">{{ periodoInfo }}</span></p>
        </div>
      </div>

      <div class="flex gap-2">
        <button @click="limpiarSeleccionNoGuardada" class="btn-secondary" :disabled="loading">
           🧹 Limpiar Cambios
        </button>
        <button @click="guardarProgramacion" class="btn-primary" :disabled="saving || loading">
          {{ saving ? 'Guardando...' : '💾 Guardar Programación' }}
        </button>
      </div>
    </div>

    <div class="section-container mb-8">
        <h2 class="section-title">1. Mesa de Trabajo (Selección por Plan)</h2>
        <div class="panel-controls">
            <div class="control-group">
                <label>Plan de Estudios</label>
                <select v-model="selectedPlan" class="select-control">
                    <option v-for="p in planes" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                </select>
            </div>
            <div class="control-group">
                <label>Versión del Plan</label>
                <select v-model="selectedVersion" :disabled="!selectedPlan" class="select-control">
                    <option v-for="v in planVersiones" :key="v.id" :value="v.id">{{ v.codigo_version }}</option>
                </select>
            </div>
            <div class="control-group stats">
                <label>Nuevos por abrir</label>
                <div class="counter-box text-blue-600">
                    {{ selectedIds.filter(id => !savedInDbIds.includes(id)).length }}
                </div>
            </div>
        </div>

        <div class="table-container shadow-sm">
            <table class="data-table">
                <thead>
                    <tr>
                        <th width="50">#</th>
                        <th width="80">Ciclo</th>
                        <th>Asignatura</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="curso in cursos" :key="curso.id" 
                        :class="{ 
                            'row-saved': savedInDbIds.includes(curso.id),
                            'row-new': selectedIds.includes(curso.id) && !savedInDbIds.includes(curso.id) 
                        }"
                        @click="toggleSelection(curso.id)">
                        <td class="text-center">
                            <input type="checkbox" :checked="selectedIds.includes(curso.id)" class="checkbox-lg" @click.stop="toggleSelection(curso.id)" />
                        </td>
                        <td><span class="cycle-badge">{{ curso.ciclo }}</span></td>
                        <td>
                            <div class="flex flex-col">
                                <span class="font-medium">{{ curso.nombre }}</span>
                                <span v-if="savedInDbIds.includes(curso.id)" class="text-[10px] text-green-600 font-bold uppercase">✓ Ya registrado</span>
                            </div>
                        </td>
                        <td>
                            <span v-if="savedInDbIds.includes(curso.id)" class="badge saved">Ya está Aperturado</span>
                            <span v-else-if="selectedIds.includes(curso.id)" class="badge new">Para guardar</span>
                            <span v-else class="badge empty">Omitido</span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <div class="section-container bg-gray-50 p-6 rounded-xl border-2 border-dashed border-gray-200">
        <div class="flex justify-between items-center mb-4">
            <h2 class="section-title text-gray-700">2. Cursos Aperturados en {{ periodoInfo }} (Global)</h2>
            <span class="badge-total">{{ cursosRegistrados.length }} Cursos totales</span>
        </div>

        <div v-if="cursosRegistrados.length === 0" class="text-center py-10 text-gray-400">
            No hay cursos aperturados oficialmente en este periodo todavía.
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="curso in cursosRegistrados" :key="curso.id" class="card-aperturado">
                <div class="card-cycle">{{ curso.ciclo }}°</div>
                <div class="card-content">
                    <p class="card-name">{{ curso.nombre }}</p>
                    <p class="card-code">{{ curso.codigo }}</p>
                </div>
                <div class="card-check">✓</div>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
/* Tus estilos originales se mantienen igual */
.page-content { padding: 2rem; max-width: 1400px; margin: 0 auto; }
.view-header { display: flex; justify-content: space-between; align-items: end; margin-bottom: 1.5rem; }
.title { font-size: 1.8rem; color: #1e293b; font-weight: 700; margin: 0; }
.subtitle { color: #64748b; font-size: 0.95rem; margin: 0; }
.btn-back { display: flex; align-items: center; background: white; border: 1px solid #e2e8f0; padding: 0.5rem 1rem; border-radius: 8px; color: #64748b; cursor: pointer; }
.btn-primary { background: #4f46e5; color: white; padding: 0.7rem 1.5rem; border-radius: 8px; font-weight: 600; display: flex; align-items: center; border: none; cursor: pointer; transition: 0.2s; }
.btn-primary:disabled { background: #a5a5f2; cursor: not-allowed; }

.panel-controls { background: white; padding: 1.5rem; border-radius: 12px; display: flex; gap: 2rem; align-items: flex-end; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 1.5rem; flex-wrap: wrap; }
.control-group { flex: 1; min-width: 200px; }
.control-group.stats { flex: 0; min-width: auto; text-align: center; }
.control-group label { display: block; margin-bottom: 0.5rem; font-size: 0.85rem; font-weight: 600; color: #475569; text-transform: uppercase; }
.select-control, .input-control { width: 100%; padding: 0.6rem; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; background-color: #fff; }
.counter-box { font-size: 1.8rem; font-weight: 800; color: #4f46e5; line-height: 1; }

.table-container { background: white; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #f8fafc; padding: 1rem; text-align: left; font-size: 0.8rem; font-weight: 600; color: #64748b; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; }
.data-table td { padding: 1rem; border-bottom: 1px solid #f1f5f9; color: #334155; font-size: 0.95rem; }
.row-selected { background-color: #eff6ff; }
.row-selected td { color: #1e3a8a; }
.checkbox-lg { width: 1.2rem; height: 1.2rem; cursor: pointer; accent-color: #4f46e5; }
.cycle-badge { background: #f1f5f9; color: #475569; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 700; font-size: 0.85rem; }
.badge-type { padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
.status-badge { padding: 0.2rem 0.6rem; border-radius: 99px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
.status-badge.active { background: #dcfce7; color: #166534; }
.status-badge.inactive { background: #f1f5f9; color: #94a3b8; }
.loader-spin { border: 2px solid #f3f3f3; border-top: 2px solid #fff; border-radius: 50%; width: 14px; height: 14px; animation: spin 1s linear infinite; display: inline-block; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.row-saved {
  background-color: #f0fdf4 !important; /* Un verde muy tenue */
  border-left: 4px solid #22c55e; /* Borde verde lateral */
}

.section-title { font-size: 1.1rem; font-weight: 700; color: #334155; margin-bottom: 1rem; }

/* Estilos de la tabla de selección */
.row-saved { background-color: #f8fafc !important; cursor: default; }
.row-new { background-color: #eff6ff !important; border-left: 4px solid #3b82f6; }

/* Badges */
.badge { padding: 0.2rem 0.6rem; border-radius: 99px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }
.badge.saved { background: #dcfce7; color: #166534; }
.badge.new { background: #dbeafe; color: #1e40af; }
.badge.empty { color: #94a3b8; }

/* Tarjetas de cursos ya registrados (Sección 2) */
.card-aperturado {
    background: white;
    border: 1px solid #e2e8f0;
    padding: 1rem;
    border-radius: 10px;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.card-cycle {
    background: #4f46e5;
    color: white;
    width: 35px;
    height: 35px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    font-weight: 800;
    font-size: 0.8rem;
}
.card-name { font-weight: 600; font-size: 0.9rem; color: #1e293b; margin: 0; }
.card-code { font-size: 0.75rem; color: #64748b; margin: 0; }
.card-check { color: #22c55e; font-weight: 900; margin-left: auto; }

.badge-total { background: #334155; color: white; padding: 0.3rem 0.8rem; border-radius: 8px; font-size: 0.8rem; font-weight: 600; }

</style>