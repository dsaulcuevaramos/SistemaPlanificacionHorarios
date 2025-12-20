<script setup>
import { ref, onMounted, computed } from 'vue';
import planService from '../../api/planEstudioService';
import { useAuthStore } from '../../stores/authStore';
import Swal from 'sweetalert2';


//exclusivo para malla
import MallaCurricularModal from '../../components/MallaCurricularView.vue';
// Estado para controlar el modal de malla
const showMallaModal = ref(false);
const selectedVersionForMalla = ref(null);
const selectedPlanNombre = ref('');
// Función para abrir la malla
const openMalla = (planNombre, version) => {
    selectedPlanNombre.value = `${planNombre} - ${version.codigo_version}`;
    selectedVersionForMalla.value = version.id;
    showMallaModal.value = true;
};


// --- ESTADOS ---
const planes = ref([]);
const loading = ref(true);
const searchTerm = ref('');

// Control de la jerarquía (Maestro-Detalle)
const expandedPlans = ref({}); // { planId: boolean } para expandir/colapsar filas
const versionesCache = ref({}); // { planId: [versiones_del_plan] } para guardar datos de versiones

const authStore = useAuthStore();
const userSchoolId = authStore.user?.id_escuela;

// Modal para Plan
const showPlanModal = ref(false);
const isEditingPlan = ref(false);
const planForm = ref({
    id: null,
    codigo: '',
    nombre: '',
    anio: new Date().getFullYear(),
    estado: 1,
    id_escuela: userSchoolId, 
});

// Modal para Versión
const showVersionModal = ref(false);
const isEditingVersion = ref(false);
const currentParentPlanId = ref(null); // ID del Plan padre al crear/editar una versión
const versionForm = ref({
    id: null,
    codigo_version: '',
    fecha_vigencia: '', // Podría ser una cadena de fecha
    estado: 1,
    id_plan_estudio: null,
});


// --- LÓGICA DE CARGA Y GESTIÓN ---

const loadPlanes = async () => {
    loading.value = true;
    try {
        planes.value = await planService.getAllPlanes();
    } catch (e) {
        console.error("Error al cargar planes:", e);
        Swal.fire('Error', 'No se pudieron cargar los planes de estudio.', 'error');
    } finally {
        loading.value = false;
    }
};

// LÓGICA DE EXPANSIÓN (Carga las Versiones de forma dinámica)
const togglePlanExpand = async (planId) => {
    // 1. Colapsar si ya está abierto
    if (expandedPlans.value[planId]) {
        expandedPlans.value[planId] = false;
        return;
    }

    // 2. Expandir
    expandedPlans.value[planId] = true;

    // 3. Cargar versiones si no están en caché
    if (!versionesCache.value[planId]) {
        try {
            // Utilizamos el servicio para obtener las versiones de forma directa (asumiendo que el backend ya filtra)
            const versiones = await planService.getAllVersionesByPlan(planId);
            
            // --- CORRECCIÓN CRÍTICA: FILTRO DE SEGURIDAD EN EL FRONTEND ---
            // Si el backend no está filtrando correctamente (o devuelve versiones extra), 
            // nos aseguramos de que solo pasen aquellas cuyo campo 'id_plan_estudio' sea igual a 'planId'.
            const versionesFiltradas = versiones.filter(
                v => v.id_plan_estudio === planId
            );

            // Guardar solo las versiones correctas en el caché
            versionesCache.value[planId] = versionesFiltradas;

        } catch (e) {
            console.error(`Error cargando versiones para Plan ${planId}:`, e);
            Swal.fire('Error', 'No se pudieron cargar las versiones del plan.', 'error');
            // Aseguramos que el caché se inicialice para no intentar recargar infinitamente
            versionesCache.value[planId] = []; 
        }
    }
};

// --- CRUD PLANES ---

const openPlanModal = (plan = null) => {
    if (plan) {
        isEditingPlan.value = true;
        planForm.value = { ...plan };
    } else {
        isEditingPlan.value = false;
        planForm.value = {
            id: null,
            codigo: '',
            nombre: '',
            anio: new Date().getFullYear(),
            estado: 1,
            id_escuela: userSchoolId, 
        };
    }
    showPlanModal.value = true;
};

const savePlan = async () => {
    loading.value = true;
    console.log("Datos a enviar:", JSON.stringify(planForm.value));
    try {
        if (isEditingPlan.value) {
            await planService.updatePlan(planForm.value.id, planForm.value);
        } else {
            await planService.createPlan(planForm.value);
        }
        await loadPlanes(); // Recargar la lista principal
        Swal.fire('Guardado', 'Plan de estudio actualizado.', 'success');
        showPlanModal.value = false;
    } catch (e) {
        Swal.fire('Error', e.response?.data?.detail || 'Error al guardar el plan.', 'error');
    } finally {
        loading.value = false;
    }
};

const togglePlanStatus = async (plan) => {
    const nuevoEstado = plan.estado === 1 ? 0 : 1;
    const action = nuevoEstado === 1 ? 'activar' : 'desactivar';
    
    const result = await Swal.fire({
        title: `¿Seguro de ${action} el plan ${plan.nombre}?`,
        icon: 'warning',
        showCancelButton: true,
    });

    if (result.isConfirmed) {
        try {
            // Usamos la misma función de update
            await planService.updatePlan(plan.id, { ...plan, estado: nuevoEstado });
            await loadPlanes();
            Swal.fire('Cambiado!', `Plan ${action}do.`, 'success');
        } catch (error) {
            Swal.fire('Error', 'No se pudo cambiar el estado.', 'error');
        }
    }
};


// --- CRUD VERSIONES ---
// Lógica para abrir el modal de crear versión
const openVersionModal = (parentPlanId, version = null) => {
    currentParentPlanId.value = parentPlanId;
    
    if (version) {
        isEditingVersion.value = true;
        versionForm.value = { ...version };
    } else {
        isEditingVersion.value = false;
        versionForm.value = {
            id: null,
            codigo_version: `V-${new Date().getFullYear()}`, // Valor inicial
            fecha_vigencia: new Date().toISOString().slice(0, 10), // Fecha actual
            estado: 1,
            id_plan_estudio: parentPlanId,
        };
    }
    showVersionModal.value = true;
};

const saveVersion = async () => {
    loading.value = true;
    try {
        if (isEditingVersion.value) {
            await planService.updateVersion(versionForm.value.id, versionForm.value);
        } else {
            await planService.createVersion(versionForm.value);
        }
        
        // Refrescar el caché para que se actualice la lista de versiones
        versionesCache.value[currentParentPlanId.value] = null; // Invalida el caché
        await togglePlanExpand(currentParentPlanId.value); // Forzar la recarga
        
        Swal.fire('Guardado', 'Versión actualizada.', 'success');
        showVersionModal.value = false;
    } catch (e) {
        Swal.fire('Error', e.response?.data?.detail || 'Error al guardar la versión.', 'error');
    } finally {
        loading.value = false;
    }
};

const toggleVersionStatus = async (version) => {
    const nuevoEstado = version.estado === 1 ? 0 : 1;
    const action = nuevoEstado === 1 ? 'activar' : 'desactivar';
    
    const result = await Swal.fire({
        title: `¿Seguro de ${action} la versión ${version.codigo_version}?`,
        icon: 'warning',
        showCancelButton: true,
    });

    if (result.isConfirmed) {
        try {
            await planService.updateVersion(version.id, { ...version, estado: nuevoEstado });
            
            // Refrescar solo la lista de versiones de ese plan padre
            versionesCache.value[version.id_plan_estudio] = null;
            await togglePlanExpand(version.id_plan_estudio); 
            
            Swal.fire('Cambiado!', `Versión ${action}da.`, 'success');
        } catch (error) {
            Swal.fire('Error', 'No se pudo cambiar el estado de la versión.', 'error');
        }
    }
};

// --- FILTRO Y MONTAJE ---
const filteredPlanes = computed(() => {
    if (!searchTerm.value) return planes.value;
    const term = searchTerm.value.toLowerCase();
    return planes.value.filter(p => 
        p.nombre.toLowerCase().includes(term) || 
        String(p.anio).includes(term)
    );
});

onMounted(() => loadPlanes());

</script>

<template>
    <div class="page-content">
        <div class="view-header">
            <div>
                <h1 class="title">Planes de Estudio</h1>
                <p class="subtitle">Gestión de Planes y sus Versiones.</p>
            </div>
            <!--
            <button class="btn-primary" @click="openPlanModal()">
                <span class="icon">+</span> Nuevo Plan
            </button>
            -->
        </div>

        <div class="toolbar">
            <input v-model="searchTerm" type="text" placeholder="Buscar Plan por nombre o año..." class="search-input" />
            <span class="counter">{{ filteredPlanes.length }} Planes</span>
        </div>

        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th width="50"></th>
                        <th>Nombre del Plan</th>
                        <th width="100">Año</th>
                        <th width="120" class="text-center">Estado</th>
                        <th width="150" class="text-right">Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-if="loading">
                        <td colspan="5" class="text-center p-4">Cargando planes...</td>
                    </tr>
                    <template v-else v-for="plan in filteredPlanes" :key="plan.id">
                        <tr :class="{'row-disabled': plan.estado === 0}">
                            <td class="text-center">
                                <button class="btn-icon" @click="togglePlanExpand(plan.id)">
                                    {{ expandedPlans[plan.id] ? '▼' : '▶' }}
                                </button>
                            </td>
                            <td>{{ plan.nombre }}</td>
                            <td>{{ plan.anio }}</td>
                            <td class="text-center">
                                <span :class="['status-dot', plan.estado ? 'active' : 'inactive']"></span>
                                {{ plan.estado ? 'Activo' : 'Inactivo' }}
                            </td>
                            <td class="text-right">
                                <button class="btn-icon" @click="openPlanModal(plan)">✏️</button>
                                <button class="btn-icon" @click="togglePlanStatus(plan)">
                                    {{ plan.estado ? '🚫' : '✅' }}
                                </button>
                                <button class="btn-secondary ml-2" @click="openVersionModal(plan.id)">+ Versión</button>
                            </td>
                        </tr>

                        <tr v-if="expandedPlans[plan.id]">
                            <td colspan="5" class="detail-row">
                                
                                <div class="version-list">
                                    <h4 class="version-header">Versiones del Plan:</h4>
                                    <table class="versions-table">
                                        <thead>
                                            <tr>
                                                <th>Código</th>
                                                <th>Vigencia</th>
                                                <th class="text-center">Estado</th>
                                                <th class="text-right">Acciones</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr v-if="!versionesCache[plan.id]">
                                                <td colspan="4" class="text-center">Cargando versiones...</td>
                                            </tr>
                                            <tr v-else-if="versionesCache[plan.id].length === 0">
                                                <td colspan="4" class="text-center">No hay versiones para este plan.</td>
                                            </tr>
                                            <tr v-else v-for="version in versionesCache[plan.id]" :key="version.id" :class="{'row-disabled': version.estado === 0}">
                                                <td>{{ version.codigo_version }}</td>
                                                <td>{{ version.fecha_vigencia }}</td>
                                                <td class="text-center">
                                                     <span :class="['status-dot', version.estado ? 'active' : 'inactive']"></span>
                                                    {{ version.estado ? 'Vigente' : 'Obsoleto' }}
                                                </td>
                                                <td class="text-left">
                                                    <button class="btn-icon" title="Ver Malla Curricular" @click="openMalla(plan.nombre, version)">
                                                        📅
                                                    </button>                                                                       
                                                    <button class="btn-icon" @click="openVersionModal(plan.id, version)">✏️</button>
                                                    <button class="btn-icon" @click="toggleVersionStatus(version)">
                                                        {{ version.estado ? '🚫' : '✅' }}
                                                    </button>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </td>
                        </tr>
                    </template>
                </tbody>
            </table>
        </div>

        <div v-if="showPlanModal" class="modal-backdrop" @click.self="showPlanModal = false">
            <div class="modal-panel">
                <form @submit.prevent="savePlan" class="modal-body">
                    <h3>{{ isEditingPlan ? 'Editar Plan' : 'Crear Nuevo Plan' }}</h3>
                    
                    <div class="form-group">
                        <label>Codigo del Plan*</label>
                        <input v-model="planForm.codigo" type="text" required />
                    </div>
                    
                    <div class="form-group">
                        <label>Nombre del Plan *</label>
                        <input v-model="planForm.nombre" type="text" required />
                    </div>
                    
                    <div class="form-group">
                        <label>Año de Aprobación *</label>
                        <input v-model.number="planForm.anio" type="number" min="1900" :max="new Date().getFullYear()" required />
                    </div>

                    <div class="modal-footer">
                        <button type="button" class="btn-secondary" @click="showPlanModal = false">Cancelar</button>
                        <button type="submit" class="btn-primary">Guardar</button>
                    </div>
                </form>
            </div>
        </div>

        <div v-if="showVersionModal" class="modal-backdrop" @click.self="showVersionModal = false">
            <div class="modal-panel">
                <form @submit.prevent="saveVersion" class="modal-body">
                    <h3>{{ isEditingVersion ? 'Editar Versión' : 'Crear Nueva Versión' }}</h3>
                    
                    <div class="form-group">
                        <label>Código de Versión *</label>
                        <input v-model="versionForm.codigo_version" type="text" required placeholder="Ej. V-2024" />
                    </div>
                    <div class="form-group">
                        <label>Fecha de Vigencia *</label>
                        <input v-model="versionForm.fecha_vigencia" type="date" required />
                    </div>

                    <div class="modal-footer">
                        <button type="button" class="btn-secondary" @click="showVersionModal = false">Cancelar</button>
                        <button type="submit" class="btn-primary">Guardar</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    <MallaCurricularModal 
    :show="showMallaModal"
    :plan-version-id="selectedVersionForMalla"
    :plan-nombre="selectedPlanNombre"
    @close="showMallaModal = false"
/>
</template>

<style scoped>
/* Estilos Base (Reutiliza tus estilos de CursosView y DocentesView) */
.page-content { padding: 2rem; max-width: 1400px; margin: 0 auto; }
.view-header { display: flex; justify-content: space-between; align-items: end; margin-bottom: 2rem; }
.title { font-size: 1.8rem; font-weight: 700; margin: 0; color: #1e293b; }
.subtitle { color: #64748b; font-size: 0.95rem; margin: 0; }
.btn-primary { background: #3b82f6; color: white; padding: 10px 20px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; }
.btn-secondary { background: white; border: 1px solid #cbd5e1; color: #334155; padding: 10px 20px; border-radius: 8px; cursor: pointer; }

/* Toolbar */
.toolbar { display: flex; justify-content: space-between; align-items: center; background: white; padding: 1rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 1.5rem; }
.search-input { padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; width: 350px; }
.counter { color: #64748b; font-size: 0.9rem; font-weight: 500; }

/* Tabla */
.table-container { background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #f8fafc; padding: 1rem; color: #475569; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; }
.data-table td { padding: 0.8rem 1rem; border-bottom: 1px solid #f1f5f9; vertical-align: middle; font-size: 0.95rem; }
.data-table tr:hover:not(.detail-row) { background-color: #f8fafc; }

/* Iconos de estado y acciones */
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 5px; }
.status-dot.active { background: #22c55e; }
.status-dot.inactive { background: #cbd5e1; }
.row-disabled { opacity: 0.6; }
.btn-icon { background: none; border: none; font-size: 1.1rem; cursor: pointer; padding: 5px; }

/* Estilos de la Fila Detalle */
.detail-row { padding: 0 !important; background: #fdfefe; border-top: 2px solid #e2e8f0; }
.version-list { padding: 1rem 3rem 1rem 3rem; }
.version-header { font-size: 1rem; color: #334155; margin-bottom: 0.8rem; border-bottom: 1px solid #f1f5f9; padding-bottom: 5px; }
.versions-table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 4px rgba(0,0,0,0.05); border-radius: 8px; overflow: hidden; }
.versions-table th { background: #f4f5f7; padding: 0.5rem; font-size: 0.8rem; color: #64748b; }
.versions-table td { padding: 0.5rem; border-bottom: 1px solid #f8fafc; }

/* Modal */
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 100; }
.modal-panel { background: white; width: 100%; max-width: 500px; border-radius: 16px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); overflow: hidden; }
.modal-body { padding: 1.5rem; }
.modal-body h3 { margin-top: 0; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 1rem; color: #1e293b; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 0.4rem; }
.form-group input { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 8px; outline: none; }
.modal-footer { padding-top: 1rem; display: flex; justify-content: flex-end; gap: 1rem; border-top: 1px solid #f1f5f9; }
</style>