<script setup>
import { ref, computed, onMounted } from 'vue';
import docenteService from '../../api/docenteService'; 
import Swal from 'sweetalert2';  //para que se vea bien princesa las alertas
import { useAuthStore } from '../../stores/authStore'; // Necesario para obtener id_escuela

// --- ESTADO ---
const docentes = ref([]);
const loading = ref(true);
const searchTerm = ref('');
const showModal = ref(false);
const isEditing = ref(false);


// Obtenemos la id_escuela del usuario logueado (necesario para la creación)
const authStore = useAuthStore();
const userSchoolId = computed(() => {
  return authStore.user?.id_escuela; 
});

// Objeto Formulario
const form = ref({
  id: null,
  nombre: '',
  apellido: '',
  dni: '',
  email: '',
  telefono: '',
  tipo_docente: 'CONTRATADO',
  horas_maximas_semanales: 20,
  id_escuela: userSchoolId, // CRÍTICO: Asignar la escuela del usuario
  estado: 1 // Asegurar el estado inicial para la creación
});

// --- CARGA DE DATOS ---
const loadDocentes = async () => {
  loading.value = true;
  try {
    // Llamada al Backend Real
    // El backend se encarga del filtro multi-tenant.
    docentes.value = await docenteService.getAll(); 
  } catch (error) {
    console.error("Error cargando docentes desde el Backend:", error);
    // Mostrar un mensaje de error o dejar el array vacío
    Swal.fire('Error', 'No se pudieron cargar los datos de los docentes. Revise la conexión.', 'error');
  } finally {
    loading.value = false;
  }
};

onMounted(() => loadDocentes());

// --- FILTRO (BUSCADOR) ---
const filteredDocentes = computed(() => {
    if (!searchTerm.value) return docentes.value;
    const term = searchTerm.value.toLowerCase();
    return docentes.value.filter(d => 
        d.nombre.toLowerCase().includes(term) || 
        d.apellido.toLowerCase().includes(term) ||
        d.dni.includes(term)
    );
});

// --- LÓGICA DEL MODAL ---
const openModal = (docente = null) => {
  
  if (docente) {
    isEditing.value = true;
    form.value = { ...docente }; // Clonamos el objeto
  } else {
    isEditing.value = false;
    form.value = { // CRÍTICO: Resetear e incluir id_escuela
      nombre: '', apellido: '', dni: '', email: '', 
      telefono: '', tipo_docente: 'CONTRATADO', 
      horas_maximas_semanales: 20, estado: 1, id_escuela: userSchoolId 
    };
  }
  showModal.value = true;
};

const closeModal = () => showModal.value = false;

// --- GUARDAR (CREATE / UPDATE) ---
const saveDocente = async () => {
  loading.value = true;
  authStore.error = null; // Limpiamos el error del store si existe

  try {
    if (isEditing.value) {
      await docenteService.update(form.value.id, form.value);
    } else {
      await docenteService.create(form.value);
    }
    
    // Éxito:
    await loadDocentes();
    closeModal();
    Swal.fire('Guardado', 'Docente registrado exitosamente.', 'success');

  } catch (error) {
    // El error.response?.data?.detail viene del servicio
    const detail = error.response?.data?.detail || 'Ocurrió un error desconocido.';
    Swal.fire('Error al guardar', detail, 'error');
  } finally {
    loading.value = false;
  }
};

// --- ESTADO (Activar/Desactivar) ---
const toggleStatus = async (docente) => {
  const nuevoEstado = docente.estado === 1 ? 0 : 1;
  const action = nuevoEstado === 1 ? 'activar' : 'desactivar';

  const result = await Swal.fire({
    title: `¿Seguro de ${action} a ${docente.nombre}?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: `Sí, ${action}!`
  });

  if (result.isConfirmed) {
      try {
          // Enviamos el objeto completo con el nuevo estado       
          await docenteService.toggleStatus(docente.id, { ...docente, estado: nuevoEstado }); 
          await loadDocentes();

          //docente.estado = nuevoEstado; // Actualización optimista
          Swal.fire('Cambiado!', `El docente ha sido ${action}do.`, 'success');
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
        <h1 class="title">Gestión de Docentes</h1>
        <p class="subtitle">Administre la plana docente, contratos y carga horaria.</p>
      </div>
      <button class="btn-primary" @click="openModal()">
        <span class="icon">+</span> Nuevo Docente
      </button>
    </div>

    <div class="toolbar">
      <div class="search-container">
        <span class="search-icon">🔍</span>
        <input 
          v-model="searchTerm" 
          type="text" 
          placeholder="Buscar por Nombre, Apellido o DNI..." 
          class="search-input"
        />
      </div>
      <div class="filters">
        <span class="counter">{{ filteredDocentes.length }} Docentes encontrados</span>
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Docente</th>
            <th>DNI / Contacto</th>
            <th>Tipo</th>
            <th>Carga Max.</th>
            <th>Estado</th>
            <th class="actions-col">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="6" class="text-center py-4">Cargando datos...</td>
          </tr>
          <tr v-else-if="filteredDocentes.length === 0">
            <td colspan="6" class="text-center py-4">No se encontraron docentes.</td>
          </tr>
          
          <tr v-for="doc in filteredDocentes" :key="doc.id" :class="{'row-disabled': doc.estado === 0}">
            <td>
              <div class="user-cell">
                <div class="avatar-circle">{{ doc.nombre[0] }}{{ doc.apellido[0] }}</div>
                <div class="user-info">
                  <span class="font-bold">{{ doc.apellido }}, {{ doc.nombre }}</span>
                  <span class="email-text">{{ doc.email }}</span>
                </div>
              </div>
            </td>
            <td>
              <div class="contact-info">
                <span>🆔 {{ doc.dni }}</span>
                <span v-if="doc.telefono">📞 {{ doc.telefono }}</span>
              </div>
            </td>
            <td>
              <span :class="['badge', doc.tipo_docente === 'NOMBRADO' ? 'badge-blue' : 'badge-orange']">
                {{ doc.tipo_docente }}
              </span>
            </td>
            <td>{{ doc.horas_maximas_semanales }} hrs</td>
            <td>
              <span :class="['status-dot', doc.estado === 1 ? 'status-active' : 'status-inactive']"></span>
              {{ doc.estado === 1 ? 'Activo' : 'Inactivo' }}
            </td>
            <td class="actions-col">
              <button class="btn-icon edit" title="Editar" @click="openModal(doc)">✏️</button>
              <button class="btn-icon toggle" title="Cambiar Estado" @click="toggleStatus(doc)">
                {{ doc.estado === 1 ? '🚫' : '✅' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal-panel">
        <div class="modal-header">
          <h3>{{ isEditing ? 'Editar Docente' : 'Registrar Nuevo Docente' }}</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        
        <form @submit.prevent="saveDocente" class="modal-body">
          <div class="grid-2">
            <div class="form-group">
              <label>DNI *</label>
              <input v-model="form.dni" type="text" maxlength="15" required :disabled="isEditing" />
            </div>
            <div class="form-group">
              <label>Tipo *</label>
              <select v-model="form.tipo_docente" required>
                <option value="NOMBRADO">Nombrado</option>
                <option value="CONTRATADO">Contratado</option>
              </select>
            </div>
          </div>

          <div class="grid-2">
            <div class="form-group">
              <label>Nombres *</label>
              <input v-model="form.nombre" type="text" required />
            </div>
            <div class="form-group">
              <label>Apellidos *</label>
              <input v-model="form.apellido" type="text" required />
            </div>
          </div>

          <div class="grid-2">
            <div class="form-group">
              <label>Email</label>
              <input v-model="form.email" type="email" />
            </div>
            <div class="form-group">
              <label>Teléfono</label>
              <input v-model="form.telefono" type="text" />
            </div>
          </div>

          <div class="form-group">
            <label>Carga Horaria Máxima Semanal</label>
            <input v-model="form.horas_maximas_semanales" type="number" min="0" max="40" />
            <small class="help-text">Tope base para el algoritmo de asignación.</small>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
            <button type="submit" class="btn-primary" :disabled="loading">
              {{ loading ? 'Guardando...' : 'Guardar Datos' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* --- LAYOUT --- */
.page-content {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* --- HEADER --- */
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.title { font-size: 1.8rem; color: #1e293b; font-weight: 700; margin-bottom: 0.2rem; }
.subtitle { color: #64748b; font-size: 0.95rem; }

/* --- TOOLBAR --- */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  margin-bottom: 1.5rem;
}
.search-container { position: relative; width: 350px; }
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; }
.search-input {
  width: 100%; padding: 10px 10px 10px 38px; border: 1px solid #e2e8f0; border-radius: 8px; outline: none; transition: 0.2s;
}
.search-input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
.counter { color: #64748b; font-size: 0.9rem; font-weight: 500; }

/* --- TABLE --- */
.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  overflow: hidden; /* Round corners */
}
.data-table { width: 100%; border-collapse: collapse; }
.data-table th {
  background: #f8fafc; text-align: left; padding: 1rem; color: #475569; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e2e8f0;
}
.data-table td { padding: 1rem; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
.data-table tr:hover { background-color: #f8fafc; }

/* Celdas Específicas */
.user-cell { display: flex; align-items: center; gap: 12px; }
.avatar-circle {
  width: 36px; height: 36px; background: #e0e7ff; color: #4f46e5; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem;
}
.user-info { display: flex; flex-direction: column; }
.email-text { font-size: 0.8rem; color: #64748b; }
.contact-info { display: flex; flex-direction: column; font-size: 0.85rem; color: #334155; }

/* Badges y Status */
.badge { padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
.badge-blue { background: #dbeafe; color: #1e40af; }
.badge-orange { background: #ffedd5; color: #9a3412; }

.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-active { background: #22c55e; }
.status-inactive { background: #cbd5e1; }
.row-disabled { opacity: 0.6; background-color: #f9fafb; }

/* Botones */
.btn-primary { background: #3b82f6; color: white; padding: 10px 20px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: 0.2s; }
.btn-primary:hover { background: #2563eb; }
.btn-secondary { background: white; border: 1px solid #cbd5e1; color: #334155; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
.btn-icon { background: none; border: none; font-size: 1.1rem; cursor: pointer; padding: 6px; border-radius: 4px; transition: 0.2s; }
.btn-icon:hover { background: #f1f5f9; }

/* --- MODAL --- */
.modal-backdrop {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px);
  display: flex; justify-content: center; align-items: center; z-index: 100;
}
.modal-panel {
  background: white; width: 100%; max-width: 600px; border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); overflow: hidden;
  animation: modalPop 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes modalPop { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }

.modal-header { padding: 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { font-size: 1.25rem; color: #1e293b; margin: 0; }
.close-btn { background: none; border: none; font-size: 1.5rem; color: #64748b; cursor: pointer; }

.modal-body { padding: 1.5rem; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { margin-bottom: 1.2rem; }
.form-group label { display: block; font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 0.4rem; }
.form-group input, .form-group select {
  width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; outline: none;
}
.form-group input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
.help-text { font-size: 0.75rem; color: #94a3b8; margin-top: 4px; display: block; }

.modal-footer { padding-top: 1rem; display: flex; justify-content: flex-end; gap: 1rem; border-top: 1px solid #f1f5f9; }
</style>