<script setup>
import { ref, computed, onMounted } from 'vue';
import aulaService from '../../api/aulaService';
import catalogoService from '../../api/catalogoService';  
import Swal from 'sweetalert2'
import { useAuthStore } from '../../stores/authStore';

// --- ESTADO ---
const aulas = ref([]);
const loading = ref(true);
const searchTerm = ref('');
const showModal = ref(false);
const isEditing = ref(false);

const tipoAula = ref([]);
const recursosOptions = ['Proyector', 'Aire Acondicionado', 'Pizarra Acrílica', 'Computadoras', 'Internet', 'Audio'];// Lista de recursos disponibles para marcar

const authStore = useAuthStore();
const userEscuelaId = computed(() => {
  return authStore.user?.id_escuela; 
});

//--refernecia de datos---
const form = ref({
  id: null, 
  nombre: '', 
  pabellon: '', 
  aforo: 40,
  tipo_aula: '',
  id_escuela: '',
  recursos: [],
  estado: 1, 
  piso: 1
});

//-- iniciar datos de catalogo --
const initAula = async () => {
  loading.value = true;
  try{
    const [tipoData] = await Promise.all([
      catalogoService.getByTableName('TIPO_AULA')
    ]);
    tipoAula.value = tipoData;

    await loadAulas();
  }catch (error) {
      console.error("Error al inicializar data:", error);
      Swal.fire('Error', 'Error al cargar catálogos.', 'error');
  } finally {
        loading.value = false;
  }
};

// --- CARGA ---
const loadAulas = async () => {
   loading.value = true;
  try {
    aulas.value = await aulaService.getAll(); 
  } catch (error) {
    console.error("Error cargando aulas desde el Backend:", error);
    // Mostrar un mensaje de error o dejar el array vacío
    Swal.fire('Error', 'No se pudieron cargar los datos de las aulas. Revise la conexión.', 'error');
  } finally {
    loading.value = false;
  }
};

onMounted(() => initAula());

const filteredAulas = computed(() => {
  if (!searchTerm.value) return aulas.value;
  const term = searchTerm.value.toLowerCase();
  return aulas.value.filter(a => 
    a.nombre.toLowerCase().includes(term) || 
    a.pabellon.toLowerCase().includes(term)
  );
});

// --- MODAL ---
const openModal = (aula = null) => {
  console.log("Objeto User completo:", authStore.user);
  console.log("ID Escuela intentando leer:", authStore.user?.id_escuela);
  if (aula) {
    isEditing.value = true;
    form.value = { ...aula, recursos: [...aula.recursos] };
  } else {
    isEditing.value = false;
    form.value = { 
      nombre: '', 
      pabellon: '', 
      aforo: 40, 
      tipo_aula: '', // O el valor por defecto si prefieres: tipoAula.value[0]?.codigo 
      id_escuela: userEscuelaId.value, // <--- CRÍTICO: Usar el ID calculado arriba
      recursos: [], 
      estado: 1,
      piso: 1
    };
  }
  showModal.value = true;
};

const closeModal = () => showModal.value = false;


const saveAula = async () => {;
  const escuelaIdActual = authStore.user?.id_escuela;

  // 2. VALIDACIÓN ESTRICTA
  if (!escuelaIdActual) {
    console.error("ERROR CRÍTICO: AuthStore sin datos de usuario.");
    Swal.fire({
      title: 'Error de Sesión',
      text: 'No se detecta tu escuela. Es posible que tu sesión haya caducado o no se cargaron los datos. Por favor recarga la página (F5).',
      icon: 'error'
    });
    return; // Detenemos todo aquí.
  }
  loading.value = true;
  authStore.error = null;
  try{
    const payload = {
      ...form.value,
      id_escuela: escuelaIdActual 
    };
    if (isEditing.value) {
        await aulaService.update(payload.id, form.value);
      } else {
        await aulaService.create(payload);
      }
      await loadAulas();
      closeModal();
      Swal.fire('Guardado', 'Aula registrada exitosamente.', 'success');

  }catch (error) {
    const detail = error.response?.data?.detail || 'Error al guardar el aula.';
    Swal.fire('Error al guardar', detail, 'error');
  } finally {
    loading.value = false;
  }
};

const toggleStatus = async (aula) => {
  const nuevoEstado = aula.estado === 1? 0 : 1;
  const action = nuevoEstado === 1? 'activar' : 'desactivar'
  const resultado = await Swal.fire({
    title: `¿Seguro de ${action} el aula?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: `Sí, ${action}!`
  });
  if (resultado.isConfirmed) {
        try {
            await aulaService.toggleStatus(aula.id, { ...aula, estado: nuevoEstado }); 
            await loadAulas(); 
            Swal.fire('Éxito', `aula ${action}da.`, 'success');
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
        <h1 class="title">Infraestructura y Aulas</h1>
        <p class="subtitle">Gestión de espacios físicos y equipamiento.</p>
      </div>
      <button class="btn-primary" @click="openModal()">
        <span class="icon">+</span> Nueva Aula
      </button>
    </div>

    <div class="toolbar">
      <div class="search-container">
        <span class="search-icon">🔍</span>
        <input v-model="searchTerm" type="text" placeholder="Buscar por nombre o pabellón..." class="search-input" />
      </div>
      <div class="filters">
        <span class="counter">{{ filteredAulas.length }} Espacios registrados</span>
      </div>
    </div>

    <div class="cards-layout">
      <div v-if="loading" class="p-5 text-center">Cargando...</div>

      <div v-for="aula in filteredAulas" :key="aula.id" :class="['aula-item', {'disabled': aula.estado === 0}]">
        
        <div class="aula-icon" :class="aula.tipo_aula === 'LABORATORIO' ? 'bg-indigo' : 'bg-orange'">
          {{ aula.tipo_aula === 'LABORATORIO' ? '🖥️' : '🏫' }}
        </div>

        <div class="aula-info">
          <div class="info-header">
            <h3>{{ aula.nombre }}</h3>
            <span class="location-badge">{{ aula.pabellon }} - Piso {{ aula.piso }}</span>
          </div>
          
          <div class="info-details">
            <span class="cap-badge">👥 {{ aula.aforo }} Personas</span>
            <span :class="['type-badge', aula.tipo_aula === 'LABORATORIO' ? 'text-indigo' : 'text-orange']">
                {{ aula.tipo_aula }} 
            </span>
          </div>

          <div class="resources-list">
            <span v-for="rec in aula.recursos" :key="rec" class="res-tag">
              • {{ rec }}
            </span>
            <span v-if="aula.recursos.length === 0" class="no-res">Sin equipamiento esp.</span>
          </div>
        </div>

        <div class="aula-actions">
          <button class="btn-icon" @click="openModal(aula)">✏️</button>
          <button class="btn-icon" @click="toggleStatus(aula)">
            {{ aula.estado ? '🚫' : '✅' }}
          </button>
        </div>

      </div>
    </div>

    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal-panel">
        <div class="modal-header">
          <h3>{{ isEditing ? 'Editar Ambiente' : 'Nuevo Ambiente' }}</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        
        <form @submit.prevent="saveAula" class="modal-body">
          
          <div class="grid-2">
            <div class="form-group">
              <label>Nombre del Aula *</label>
              <input v-model="form.nombre" type="text" required placeholder="Ej. Aula 101" />
            </div>
            <div class="form-group">
              <label>Tipo *</label>
              <select v-model="form.tipo_aula" required>
                 <option v-for="tipo in tipoAula" :key="tipo.id" :value="tipo.codigo">
                    {{ tipo.descripcion }}
                 </option>
              </select>
            </div>
          </div>
          
          <div class="grid-3">
            <div class="form-group">
              <label>Pabellón *</label>
              <input v-model="form.pabellon" type="text" required placeholder="Ej. B" />
            </div>
            <div class="form-group">
              <label>Piso *</label>
              <input v-model.number="form.piso" type="number" min="1" required />
            </div>
            <div class="form-group">
              <label>Aforo Max. *</label>
              <input v-model.number="form.aforo" type="number" min="1" required />
            </div>
          </div>

          <div class="form-group">
            <label>Equipamiento y Recursos</label>
            <div class="checkbox-grid">
              <label v-for="opt in recursosOptions" :key="opt" class="check-label">
                <input type="checkbox" :value="opt" v-model="form.recursos">
                {{ opt }}
              </label>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
            <button type="submit" class="btn-primary" :disabled="loading">
                {{ loading ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* REUTILIZAR ESTILOS BASE + NUEVOS PARA AULAS */
.page-content { padding: 2rem; max-width: 1200px; margin: 0 auto; }
.view-header { display: flex; justify-content: space-between; align-items: end; margin-bottom: 2rem; }
.title { font-size: 1.8rem; color: #1e293b; font-weight: 700; margin: 0; }
.subtitle { color: #64748b; font-size: 0.95rem; margin: 0; }

.toolbar { display: flex; justify-content: space-between; align-items: center; background: white; padding: 1rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 1.5rem; }
.search-container { position: relative; width: 350px; }
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; }
.search-input { width: 100%; padding: 10px 10px 10px 38px; border: 1px solid #e2e8f0; border-radius: 8px; outline: none; transition: 0.2s; }
.search-input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
.counter { color: #64748b; font-size: 0.9rem; font-weight: 500; }

/* LISTA TIPO TARJETAS HORIZONTALES */
.cards-layout { display: flex; flex-direction: column; gap: 1rem; }

.aula-item {
  display: flex; align-items: center; background: white; padding: 1.5rem;
  border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); border: 1px solid #f1f5f9;
  transition: transform 0.2s;
}
.aula-item:hover { transform: translateX(5px); border-color: #e2e8f0; }
.aula-item.disabled { opacity: 0.6; background: #f8fafc; }

.aula-icon {
  width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-right: 1.5rem; flex-shrink: 0;
}
.bg-indigo { background: #e0e7ff; }
.bg-orange { background: #ffedd5; }

.aula-info { flex: 1; }
.info-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem; }
.info-header h3 { margin: 0; font-size: 1.1rem; color: #334155; }
.location-badge { background: #f1f5f9; color: #64748b; font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; font-weight: 600; }

.info-details { display: flex; gap: 1rem; margin-bottom: 0.5rem; font-size: 0.85rem; }
.cap-badge { color: #475569; font-weight: 500; }
.type-badge { font-weight: 700; font-size: 0.75rem; text-transform: uppercase; }
.text-indigo { color: #4338ca; }
.text-orange { color: #c2410c; }

.resources-list { display: flex; gap: 8px; flex-wrap: wrap; }
.res-tag { font-size: 0.75rem; color: #64748b; background: #f8fafc; padding: 2px 6px; border-radius: 4px; border: 1px solid #e2e8f0; }
.no-res { font-size: 0.75rem; color: #94a3b8; font-style: italic; }

.aula-actions { display: flex; gap: 8px; }

/* BOTONES COMUNES */
.btn-primary { background: #3b82f6; color: white; padding: 10px 20px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; }
.btn-icon { background: white; border: 1px solid #e2e8f0; font-size: 1.1rem; cursor: pointer; padding: 8px; border-radius: 8px; transition: 0.2s; }
.btn-icon:hover { background: #f1f5f9; border-color: #cbd5e1; }
.btn-secondary { background: white; border: 1px solid #cbd5e1; color: #334155; padding: 10px 20px; border-radius: 8px; cursor: pointer; }

/* MODAL & FORMULARIO */
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 100; }
.modal-panel { background: white; width: 100%; max-width: 600px; border-radius: 16px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); overflow: hidden; }
.modal-header { padding: 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.close-btn { background: none; border: none; font-size: 1.5rem; color: #64748b; cursor: pointer; }
.modal-body { padding: 1.5rem; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 0.4rem; }
.form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 8px; outline: none; }

/* Checkboxes de Recursos */
.checkbox-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; background: #f8fafc; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; }
.check-label { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; color: #334155; cursor: pointer; }
.check-label input { width: auto; }

.modal-footer { padding-top: 1rem; display: flex; justify-content: flex-end; gap: 1rem; border-top: 1px solid #f1f5f9; }
</style>