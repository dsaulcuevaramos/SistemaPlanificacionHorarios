<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import cursoService from '../../api/cursoService'; 
import planService from '../../api/planEstudioService';   
import catalogoService from '../../api/catalogoService';  
import Swal from 'sweetalert2';
import { useAuthStore } from '../../stores/authStore';

// --- ESTADO ---
// NUEVO: Estado para los planes generales
const planes = ref([]);             // Lista de Planes (Nivel 1)
const planVersiones = ref([]);      // Lista de Versiones (Nivel 2)
const cursos = ref([]);

const selectedPlan = ref(null);         // ID del Plan seleccionado
const selectedPlanVersion = ref(null);  // ID de la Versión seleccionada

const loading = ref(false);
const searchTerm = ref('');
const showModal = ref(false);
const isEditing = ref(false);

const authStore = useAuthStore();
const userSchoolId = authStore.user?.id_escuela || null; 

//de catalogo
const tiposCurso = ref([]);
const paridades = ref([]);

const form = ref({
  id: null, codigo: '', nombre: '', ciclo: 1, creditos: 3, 
  horas_teoricas: 0, horas_practicas: 0, tipo_curso: '', paridad: '',
  id_plan_version: null, 
  id_escuela: userSchoolId, 
  estado: 1
});

// --- CARGA INICIAL ---
const initData = async () => {
  loading.value = true;
  try {
    // A) Cargar Tablas Maestras y Planes Generales
    const [planesData, tiposData, paridadData] = await Promise.all([
        planService.getAllPlanes(),
        catalogoService.getByTableName('TIPO_CURSO'),
        catalogoService.getByTableName('PARIDAD')
    ]);

    planes.value = planesData;
    tiposCurso.value = tiposData;
    paridades.value = paridadData;

    // B) Seleccionar el primer plan por defecto para disparar la cascada
    if (planes.value.length > 0) {
      const ultimoPlan = planes.value.sort((a, b) => b.id - a.id)[0]
      selectedPlan.value = ultimoPlan.id;//  selectedPlan.value = planes.value[0].id; 
        // AL ASIGNAR ESTO, SE EJECUTA EL WATCHER DE ABAJO AUTOMÁTICAMENTE
    }

    // C) Cargar todos los cursos (luego se filtran en el computed)
    await loadCursos();

  } catch (e) {
    console.error("Error initData:", e);
    Swal.fire('Error', 'No se pudieron cargar los datos.', 'error');
  } finally {
    loading.value = false;
  }
};

const loadCursos = async () => {
    const data = await cursoService.getAll();
    cursos.value = data || [];
};

// --- 2. WATCHER (LA MAGIA DE LA CASCADA) ---
// Cuando cambia el PLAN -> Cargamos sus VERSIONES
watch(selectedPlan, async (newPlanId) => {
    // 1. Limpiar inmediatamente para no mostrar datos viejos
    selectedPlanVersion.value = null; 
    planVersiones.value = []; 

    if (!newPlanId) return;

    loading.value = true;
    try {
        // 2. Traer versiones del servidor
        // (Nota: idealmente el backend ya debería filtrar, pero haremos un doble chequeo)
        const data = await planService.getAllVersionesByPlan(newPlanId);

        // 3. --- EL FILTRO DE SEGURIDAD (AQUÍ ESTÁ LA SOLUCIÓN) ---
        // Verificamos que la versión pertenezca REALMENTE al plan seleccionado.
        // OJO: Revisa si en tu base de datos el campo se llama 'id_plan' o 'id_plan_estudio'
        const versionesDelPlan = data.filter(v => 
            v.id_plan_estudio === newPlanId || v.id_plan === newPlanId
        );

        // 4. Ordenar: La versión más reciente primero (ID más alto arriba)
        const versionesOrdenadas = versionesDelPlan.sort((a, b) => b.id - a.id);
        
        // 5. Asignar
        planVersiones.value = versionesOrdenadas;

        // 6. Autoseleccionar la última versión
        if (planVersiones.value.length > 0) {
            selectedPlanVersion.value = planVersiones.value[0].id;
        }

    } catch (error) {
        console.error("Error al cargar versiones:", error);
    } finally {
        loading.value = false;
    }
});

onMounted(() => initData());

// --- 3. COMPUTED (FILTRADO DE TABLA) ---
const filteredCursos = computed(() => {
  // Si no hay versión seleccionada, tabla vacía
  if (!selectedPlanVersion.value) return [];

  // Filtrar cursos que coincidan con la versión seleccionada
  let result = cursos.value.filter(c => c.id_plan_version === selectedPlanVersion.value);

  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    result = result.filter(c => 
      c.nombre.toLowerCase().includes(term) || 
      c.codigo.toLowerCase().includes(term)
    );
  }
  return result.sort((a, b) => a.ciclo - b.ciclo);
});

// --- RESTO DE FUNCIONES (MODAL, GUARDAR, ETC) ---
const openModal = (curso = null) => {
  if (!selectedPlanVersion.value && !curso) {
      Swal.fire('Aviso', 'Seleccione un Plan y una Versión primero.', 'warning');
      return;
  }
  if (curso) {
    isEditing.value = true;
    form.value = { ...curso }; 
  } else {
    isEditing.value = false;
    form.value = {
      id: null, codigo: '', nombre: '', ciclo: 1, creditos: 3, 
      horas_teoricas: 0, horas_practicas: 0, tipo_curso: '', paridad: '',
      id_plan_version: selectedPlanVersion.value, // <--- IMPORTANTE
      id_escuela: userSchoolId, 
      estado: 1
    };
  }
  showModal.value = true;
};
// ... Copia tus funciones closeModal, saveCurso y toggleStatus aquí ...
const closeModal = () => showModal.value = false;

// Observador para autocalcular paridad simple
watch(() => form.value.ciclo, (newCiclo) => {
  if (!isEditing.value && newCiclo) { 
    form.value.paridad = newCiclo % 2 === 0 ? 'PAR' : 'IMPAR';
  }
});

const saveCurso = async () => {
  loading.value = true;
  try {
    if (isEditing.value) {
      await cursoService.update(form.value.id, form.value);
    } else {
      await cursoService.create(form.value);
    }
    
    await loadCursos(); 
    closeModal();
    Swal.fire('Guardado', 'Curso registrada exitosamente.', 'success');

  } catch (error) {
    const detail = error.response?.data?.detail || 'Error al guardar el curso.';
    Swal.fire('Error al guardar', detail, 'error');
  } finally {
    loading.value = false;
  }
};

const toggleStatus = async (curso) => {
    const nuevoEstado = curso.estado === 1 ? 0 : 1;
    const action = nuevoEstado === 1 ? 'activar' : 'desactivar';

    const result = await Swal.fire({
      title: `¿Seguro de ${action} el curso?`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: `Sí, ${action}!`
    });

    if (result.isConfirmed) {
        try {
            await cursoService.toggleStatus(curso.id, { ...curso, estado: nuevoEstado }); 
            await loadCursos(); 
            Swal.fire('Éxito', `curso ${action}da.`, 'success');
        } catch (error) {
            Swal.fire('Error', 'No se pudo cambiar el estado.', 'error');
        }
    }
};

</script>

<template>
  <div class="page-content">
    
    <div class="view-header">
      <div>
        <h1 class="title">Catálogo de Cursos</h1>
        <p class="subtitle">Gestión de asignaturas por Plan de Estudios.</p>
      </div>
      <div class="header-actions">

        <div class="plan-selector">
          <label>1. Plan Estudios:</label>
          <select v-model="selectedPlan">
            <option value="" disabled>-- Seleccione Plan --</option>
            <option v-for="p in planes" :key="p.id" :value="p.id">
              {{ p.nombre }}
            </option>
          </select>
        </div>
        
        <div class="plan-selector">
          <label>2. Versión:</label>
          <select v-model="selectedPlanVersion" :disabled="!selectedPlan || planVersiones.length === 0" class="select-control">
            <option v-if="!selectedPlan" value="">← Seleccione un Plan primero</option>
            <option v-else-if="planVersiones.length === 0" value="">Sin versiones registradas</option>
            
            <option v-for="v in planVersiones" :key="v.id" :value="v.id">
              {{ v.codigo_version }} - {{ v.estado }} 
            </option>
          </select>
        </div>

        

        <button class="btn-primary" @click="openModal()" :disabled="!selectedPlanVersion">
          <span class="icon">+</span> Nuevo Curso
        </button>
      </div>
    </div>

    <div class="toolbar">
      <div class="search-container">
        <span class="search-icon">🔍</span>
        <input v-model="searchTerm" type="text" placeholder="Buscar asignatura..." class="search-input" />
      </div>
      <div class="filters">
        <span class="counter">{{ filteredCursos.length }} Asignaturas listadas</span>
      </div>
    </div>

    <div class="table-container">
      <div v-if="loading" class="p-5 text-center">Cargando...</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th width="80">Ciclo</th>
            <th>Código / Asignatura</th>
            <th>Tipo</th>
            <th>Paridad</th>
            <th class="text-center">Créditos</th>
            <th>Horas (T - P)</th>
            <th class="text-center">Estado</th>
            <th class="text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
           <tr v-if="filteredCursos.length === 0">
               <td colspan="8" class="text-center p-5 text-gray-500">
                   No hay cursos en esta versión o selecciona un plan válido.
               </td>
           </tr>

          <tr v-for="curso in filteredCursos" :key="curso.id" :class="{'row-disabled': curso.estado === 0}">
            <td>
              <div class="cycle-badge">{{ curso.ciclo }}°</div>
            </td>
            <td>
              <div class="course-info">
                <span class="code">{{ curso.codigo }}</span>
                <span class="name">{{ curso.nombre }}</span>
              </div>
            </td>
            <td>
              <span :class="['badge-type', curso.tipo_curso === 'ESPECIFICO' ? 'bg-blue' : 
                                          (curso.tipo_curso === 'GENERAL' ? 'bg-orange' : 
                                          (curso.tipo_curso === 'ESPECIALIDAD' ? 'bg-green' : 'bg-purple')) ]">
                {{ curso.tipo_curso }}
              </span>
            </td>
            <td>
              <span :class="['badge-paridad', curso.paridad === 'IMPAR' ? 'text-purple' : 'text-teal']">
                {{ curso.paridad }}
              </span>
            </td>
            <td class="text-center font-bold">{{ curso.creditos }}</td>
            <td>
              <div class="hours-pill">
                <span title="Teoría">T: {{ curso.horas_teoricas }}</span>
                <span class="divider">|</span>
                <span title="Práctica">P: {{ curso.horas_practicas }}</span>
              </div>
            </td>
            <td class="text-center">
              <span :class="['status-dot', curso.estado ? 'active' : 'inactive']"></span>
            </td>
            <td class="text-right">
              <button class="btn-icon" @click="openModal(curso)">✏️</button>
              <button class="btn-icon" @click="toggleStatus(curso)">
                {{ curso.estado ? '🚫' : '✅' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal-panel">
        <div class="modal-header">
          <h3>{{ isEditing ? 'Editar Asignatura' : 'Nueva Asignatura' }}</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        
        <form @submit.prevent="saveCurso" class="modal-body">
          
          <div class="grid-2">
            <div class="form-group">
              <label>Versión del Plan</label>
              <select v-model="form.id_plan_version" disabled class="bg-gray">
                 <option v-for="v in planVersiones" :key="v.id" :value="v.id">
                    {{ v.codigo_version }}
                 </option>
              </select>
            </div>
            <div class="form-group">
              <label>Código *</label>
              <input v-model="form.codigo" type="text" required placeholder="Ej. MAT-101" />
            </div>
          </div>

          <div class="form-group">
            <label>Nombre de la Asignatura *</label>
            <input v-model="form.nombre" type="text" required />
          </div>

          <div class="grid-3">
            <div class="form-group">
              <label>Ciclo *</label>
              <input v-model.number="form.ciclo" type="number" min="1" max="14" required />
            </div>
            <div class="form-group">
              <label>Créditos *</label>
              <input v-model.number="form.creditos" type="number" min="1" required />
            </div>
            <div class="form-group">
              <label>Paridad</label>
              <select v-model="form.paridad">
                <option v-for="p in paridades" :key="p.id" :value="p.descripcion"> 
                  {{ p.descripcion }}
                </option>
              </select>
            </div>
          </div>

          <div class="grid-3">
            <div class="form-group">
              <label>H. Teóricas</label>
              <input v-model.number="form.horas_teoricas" type="number" min="0" />
            </div>
            <div class="form-group">
              <label>H. Prácticas</label>
              <input v-model.number="form.horas_practicas" type="number" min="0" />
            </div>
            <div class="form-group">
              <label>Tipo</label>
              <select v-model="form.tipo_curso">
                <option v-for="t in tiposCurso" :key="t.id" :value="t.descripcion"> 
                  {{ t.descripcion }}
                </option>
              </select>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
            <button type="submit" class="btn-primary">Guardar</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* Solo necesitas agregar un estilo extra para que los selects se vean alineados */
.plan-selector { display: flex; flex-direction: column; gap: 5px; min-width: 200px; }
/* ... Resto de tus estilos existentes ... */
.page-content { padding: 2rem; max-width: 1400px; margin: 0 auto; }
.view-header { display: flex; justify-content: space-between; align-items: end; margin-bottom: 2rem; }
.title { font-size: 1.8rem; color: #1e293b; font-weight: 700; margin: 0; }
.subtitle { color: #64748b; font-size: 0.95rem; margin: 0; }
.header-actions { display: flex; gap: 1.5rem; align-items: end; }
.plan-selector label { font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; }
.plan-selector select { 
  padding: 8px 12px; border: 2px solid #3b82f6; border-radius: 8px; 
  background: #eff6ff; font-weight: 600; color: #1e3a8a; cursor: pointer; outline: none;
}
.toolbar { display: flex; justify-content: space-between; align-items: center; background: white; padding: 1rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 1.5rem; }
.search-container { position: relative; width: 350px; }
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; }
.search-input { width: 100%; padding: 10px 10px 10px 38px; border: 1px solid #e2e8f0; border-radius: 8px; outline: none; transition: 0.2s; }
.search-input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
.counter { color: #64748b; font-size: 0.9rem; font-weight: 500; }
.table-container { background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #f8fafc; text-align: left; padding: 1rem; color: #475569; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; }
.data-table td { padding: 0.8rem 1rem; border-bottom: 1px solid #f1f5f9; vertical-align: middle; font-size: 0.95rem; }
.data-table tr:hover { background-color: #f8fafc; }
.cycle-badge { background: #f1f5f9; color: #475569; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; border: 1px solid #e2e8f0; }
.course-info { display: flex; flex-direction: column; }
.code { font-size: 0.75rem; color: #64748b; font-weight: 700; }
.name { font-weight: 600; color: #334155; }
.badge-type { padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }
.bg-blue { background: #dbeafe; color: #1e40af; }
.bg-orange { background: #ffedd5; color: #9a3412; }
.bg-green { background: #bcf7c1; color: #129a46; }
.bg-purpple { background: #eccbd9; color: #971682d7; }
.badge-paridad { font-size: 0.75rem; font-weight: 700; }
.text-purple { color: #9333ea; background: #f3e8ff; padding: 2px 6px; border-radius: 4px; }
.text-teal { color: #0d9488; background: #ccfbf1; padding: 2px 6px; border-radius: 4px; }
.hours-pill { display: inline-flex; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 20px; padding: 4px 10px; font-size: 0.8rem; font-weight: 500; color: #475569; }
.divider { margin: 0 6px; color: #cbd5e1; }
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; }
.status-dot.active { background: #22c55e; }
.status-dot.inactive { background: #cbd5e1; }
.row-disabled { opacity: 0.5; }
.btn-primary { background: #3b82f6; color: white; padding: 10px 20px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; }
.btn-icon { background: none; border: none; font-size: 1.1rem; cursor: pointer; padding: 5px; }
.btn-icon:hover { background: #f1f5f9; border-radius: 4px; }
.btn-secondary { background: white; border: 1px solid #cbd5e1; color: #334155; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.font-bold { font-weight: 700; }
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 100; }
.modal-panel { background: white; width: 100%; max-width: 600px; border-radius: 16px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); overflow: hidden; }
.modal-header { padding: 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.modal-body { padding: 1.5rem; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 0.4rem; }
.form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 8px; outline: none; }
.bg-gray { background-color: #f1f5f9; cursor: not-allowed; }
.modal-footer { padding-top: 1rem; display: flex; justify-content: flex-end; gap: 1rem; border-top: 1px solid #f1f5f9; }
</style>