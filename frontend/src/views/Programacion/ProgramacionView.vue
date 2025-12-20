<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Swal from 'sweetalert2';
import periodoService from '../../api/periodoService';

const router = useRouter();

// ---------------------------------------------------------
// 1. ESTADO LIMPIO (Sin datos falsos)
// ---------------------------------------------------------
const periodos = ref([]); // <--- ¡Asegúrate de que esto esté VACÍO!
const loading = ref(true);
const searchTerm = ref('');
const showModal = ref(false);
const isEditing = ref(false);

const form = ref({
  id: null, codigo: '', nombre: '', descripcion: '',
  fecha_inicio: '', fecha_fin: '', estado: 1
});

// ---------------------------------------------------------
// 2. CARGA DE DATOS (CON DEBUG)
// ---------------------------------------------------------
const cargarPeriodos = async () => {
  loading.value = true;
  try {
    console.log("Pidiendo periodos al backend...");
    const data = await periodoService.getAll();
    
    console.log("Respuesta del Backend:", data); // <--- MIRA ESTO EN LA CONSOLA (F12)
    
    if (Array.isArray(data)) {
      periodos.value = data.map(p => ({
        ...p,
        estadoVisual: calcularEstadoVisual(p.fecha_inicio, p.fecha_fin, p.estado)
      }));
    }
  } catch (error) {
    console.error("Error API:", error);
    Swal.fire('Error', 'Error de conexión con el servidor.', 'error');
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  cargarPeriodos();
});

// --- RESTO DE TU LÓGICA VISUAL (Sin cambios) ---
const filteredPeriodos = computed(() => {
  if (!searchTerm.value) return periodos.value;
  const term = searchTerm.value.toLowerCase();
  return periodos.value.filter(p => 
    p.codigo.toLowerCase().includes(term) || 
    p.nombre.toLowerCase().includes(term)
  );
});

const calcularEstadoVisual = (inicio, fin, estadoDb) => {
  if (estadoDb === 0) return 'CERRADO';
  const hoy = new Date();
  const fInicio = new Date(inicio);
  const fFin = new Date(fin);
  if (hoy < fInicio) return 'EN PLANIFICACIÓN'; 
  if (hoy >= fInicio && hoy <= fFin) return 'ACTIVO';
  return 'FINALIZADO';
};

const getStatusColor = (estadoVisual) => {
  switch(estadoVisual) {
    case 'ACTIVO': return 'bg-green-100 text-green-800 border-green-200';
    case 'EN PLANIFICACIÓN': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    default: return 'bg-gray-100 text-gray-600 border-gray-200';
  }
};

const irAProgramacion = (id) => router.push(`/programacion/periodo/${id}`);
const irAContratos = (id, e) => { e.stopPropagation(); router.push(`/programacion/periodo/${id}`); };

// --- MODAL ---
const openModal = (periodo = null, e = null) => {
  if (e) e.stopPropagation();
  if (periodo) {
    isEditing.value = true;
    form.value = { ...periodo };
  } else {
    isEditing.value = false;
    form.value = { id: null, codigo: '', nombre: '', descripcion: '', fecha_inicio: '', fecha_fin: '', estado: 1 };
  }
  showModal.value = true;
};
const closeModal = () => showModal.value = false;

const savePeriodo = async () => {
  try {
    loading.value = true;
    if (isEditing.value) await periodoService.update(form.value.id, form.value);
    else await periodoService.create(form.value);
    
    await cargarPeriodos();
    closeModal();
    Swal.fire('Éxito', 'Periodo guardado', 'success');
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Error al guardar', 'error');
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="page-content dashboard-programacion">
    
    <div class="view-header">
      <div>
        <h1 class="title">Programación Académica</h1>
        <p class="subtitle">Gestione los ciclos académicos y su planificación.</p>
      </div>
      <button class="btn-primary" @click="openModal()">
        <span class="icon">+</span> Nuevo Periodo
      </button>
    </div>

    <div class="toolbar mb-6">
      <div class="search-container">
        <span class="search-icon">🔍</span>
        <input 
          v-model="searchTerm" 
          type="text" 
          placeholder="Buscar periodo (ej: 2025-I)..." 
          class="search-input"
        />
      </div>
      <div class="filters">
        <span class="counter text-gray-500 font-medium">{{ filteredPeriodos.length }} Periodos</span>
      </div>
    </div>

    <div v-if="loading" class="text-center py-10">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      <p class="text-gray-500 mt-2">Cargando datos...</p>
    </div>

    <div v-else-if="filteredPeriodos.length > 0" class="cards-grid">
      
      <div 
        v-for="periodo in filteredPeriodos" 
        :key="periodo.id"
        class="dashboard-card card-periodo"
        :class="{ 'border-l-active': periodo.estadoVisual === 'ACTIVO' }"
        @click="irAProgramacion(periodo.id)"
      >
        <div class="card-icon-bg">🗓️</div>
        
        <div class="card-body">
          <div class="flex justify-between items-center mb-3">
            
            <div class="flex items-center gap-2">
              <h3 class="text-xl font-bold text-gray-800 m-0">{{ periodo.codigo }}</h3>
              
              <button 
                @click="openModal(periodo, $event)" 
                class="btn-edit-mini"
                title="Editar Periodo"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </button>
            </div>

            <span class="text-xs font-semibold px-2 py-1 rounded border whitespace-nowrap" :class="getStatusColor(periodo.estadoVisual)">
              {{ periodo.estadoVisual }}
            </span>
          </div>
          
          <p class="description">{{ periodo.nombre }}</p>
          <p class="text-xs text-gray-400 mt-1 line-clamp-2">{{ periodo.descripcion }}</p>
          
          <ul class="features-list mt-4">
            <li><strong>Inicio:</strong> {{ periodo.fecha_inicio }}</li>
            <li><strong>Fin:</strong> {{ periodo.fecha_fin }}</li>
          </ul>
        </div>

        <div class="card-footer group">
          <div class="flex gap-2 w-full">
            <button class="flex-1 text-left text-sm font-semibold text-gray-600 group-hover:text-indigo-600 transition-colors">
              Programar <span class="arrow inline-block ml-1">→</span>
            </button>
            
            <button 
              @click="irAContratos(periodo.id, $event)"
              class="px-3 py-1 text-xs font-medium text-white bg-slate-600 rounded hover:bg-slate-700 transition-colors z-10"
              title="Gestión de Contratos Docentes"
            >
              Contratos
            </button>
          </div>
        </div>
      </div>

    </div>

    <div v-else class="text-center py-20 bg-white rounded-xl shadow-sm border border-gray-100">
      <div class="text-5xl mb-4">📭</div>
      <h3 class="text-lg font-medium text-gray-900">No hay periodos registrados</h3>
      <p class="text-gray-500">Utilice el botón "Nuevo Periodo" para comenzar.</p>
    </div>

    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal-panel">
        <div class="modal-header">
          <h3>{{ isEditing ? 'Editar Periodo' : 'Nuevo Periodo Académico' }}</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        
        <form @submit.prevent="savePeriodo" class="modal-body">
          <div class="grid-2">
            <div class="form-group">
              <label>Código *</label>
              <input 
                v-model="form.codigo" 
                type="text" 
                placeholder="Ej: 2025-I" 
                required 
                :disabled="isEditing" 
              />
            </div>
            <div class="form-group">
              <label>Nombre *</label>
              <input v-model="form.nombre" type="text" placeholder="Semestre 2025-I" required />
            </div>
          </div>

          <div class="form-group">
            <label>Descripción</label>
            <textarea v-model="form.descripcion" rows="2"></textarea>
          </div>

          <div class="grid-2">
            <div class="form-group">
              <label>Fecha Inicio *</label>
              <input v-model="form.fecha_inicio" type="date" required />
            </div>
            <div class="form-group">
              <label>Fecha Fin *</label>
              <input v-model="form.fecha_fin" type="date" required />
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
            <button type="submit" class="btn-primary" :disabled="loading">
              {{ loading ? 'Guardando...' : 'Guardar Periodo' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* Estilos Globales (Base) */
.page-content { padding: 2rem; max-width: 1400px; margin: 0 auto; }
.view-header { display: flex; justify-content: space-between; align-items: end; margin-bottom: 2rem; }
.title { font-size: 1.8rem; color: #1e293b; font-weight: 700; margin: 0; }
.subtitle { color: #64748b; font-size: 0.95rem; margin: 0; }

/* Toolbar */
.toolbar { background: white; padding: 1rem; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.search-container { display: flex; align-items: center; background: #f8fafc; padding: 0.5rem 1rem; border-radius: 8px; flex: 1; max-width: 400px; border: 1px solid #e2e8f0; }
.search-input { border: none; background: transparent; outline: none; margin-left: 0.5rem; width: 100%; color: #334155; }
.counter { font-size: 0.9rem; color: #64748b; font-weight: 500; }

/* Grid Cards */
.cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 2rem; }
.dashboard-card {
  background: white; border-radius: 16px; overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease; cursor: pointer; border: 1px solid #f1f5f9;
  position: relative; display: flex; flex-direction: column;
  border-top: 5px solid #6366f1; 
}
.dashboard-card.border-l-active { border-top-color: #10b981; }
.dashboard-card:hover { transform: translateY(-8px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }
.card-icon-bg { position: absolute; top: 1rem; right: 1rem; font-size: 4rem; opacity: 0.05; pointer-events: none; }
.card-body { padding: 1.5rem 2rem; flex: 1; } /* Ajusté el padding para que no sea tan alto */
.features-list { list-style: none; padding: 0; color: #475569; font-size: 0.85rem; }
.features-list li { margin-bottom: 5px; }

/* NUEVO: Botón editar mini (Sutil) */
.btn-edit-mini {
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    background-color: #f1f5f9; color: #94a3b8;
    border: none; cursor: pointer; transition: all 0.2s;
}
.btn-edit-mini:hover {
    background-color: #e0f2fe; color: #0284c7;
}

/* Footer Card */
.card-footer { padding: 1rem 1.5rem; background-color: #f8fafc; border-top: 1px solid #e2e8f0; display: flex; align-items: center; transition: 0.2s; }
.dashboard-card:hover .card-footer { background-color: #f0f9ff; }

/* Estilos de Modal y Botones Generales */
.btn-primary { background: #4f46e5; color: white; padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 600; display: flex; align-items: center; gap: 0.5rem; transition: 0.2s; border:none; cursor:pointer;}
.btn-primary:hover { background: #4338ca; }
.btn-secondary { background: #f1f5f9; color: #475569; padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 600; margin-right: 1rem; border:none; cursor:pointer;}
.btn-secondary:hover { background: #e2e8f0; }

.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 50; backdrop-filter: blur(2px); }
.modal-panel { background: white; width: 90%; max-width: 600px; border-radius: 16px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); overflow: hidden; animation: slideUp 0.3s ease-out; }
.modal-header { padding: 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
.modal-header h3 { font-size: 1.25rem; color: #1e293b; font-weight: 700; margin: 0; }
.close-btn { background: none; border: none; font-size: 1.5rem; color: #64748b; cursor: pointer; }
.modal-body { padding: 2rem; }
.form-group { margin-bottom: 1.2rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #475569; font-size: 0.9rem; }
.form-group input, .form-group textarea { width: 100%; padding: 0.6rem; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; transition: border-color 0.2s; }
.form-group input:focus { border-color: #6366f1; outline: none; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.modal-footer { padding: 1.5rem; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; background: #f8fafc; }

@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
</style>