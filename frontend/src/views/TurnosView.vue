<script setup>
import { ref, onMounted } from 'vue';
import turnoService from '../api/turnoService';
import Swal from 'sweetalert2';

// --- ESTADO ---
// Ya no usamos props ni watch porque la carga es directa
const turnos = ref([]);
const loading = ref(true);
const showModal = ref(false);
const isEditing = ref(false);

const form = ref({
  id: null,
  nombre: '',
  hora_inicio: '',
  hora_fin: '',
  estado: 1
});

// --- LÓGICA DE CARGA ---
const cargarTurnos = async () => {
  loading.value = true;
  try {
    console.log("Cargando turnos..."); // Para depuración en consola
    const data = await turnoService.getAll();
    turnos.value = data;
    console.log("Turnos cargados:", data);
  } catch (error) {
    console.error(error);
    Swal.fire('Error', 'No se pudieron cargar los turnos de la escuela.', 'error');
  } finally {
    loading.value = false;
  }
};

// --- MODAL ---
const openModal = (turno = null) => {
  if (turno) {
    isEditing.value = true;
    form.value = { 
      ...turno, 
      hora_inicio: formatTime(turno.hora_inicio), 
      hora_fin: formatTime(turno.hora_fin) 
    };
  } else {
    isEditing.value = false;
    form.value = { 
      id: null, nombre: '', hora_inicio: '', 
      hora_fin: '', estado: 1 
    };
  }
  showModal.value = true;
};

// --- GUARDAR ---
const saveTurno = async () => {
  if (!form.value.nombre || !form.value.hora_inicio || !form.value.hora_fin) {
    Swal.fire('Campos vacíos', 'Completa el nombre y horario.', 'warning');
    return;
  }

  // Formatear HH:MM a HH:MM:00 si es necesario
  const formatTimePayload = (t) => t.length === 5 ? `${t}:00` : t;
  
  const payload = {
    nombre: form.value.nombre,
    hora_inicio: formatTimePayload(form.value.hora_inicio),
    hora_fin: formatTimePayload(form.value.hora_fin),
    estado: form.value.estado
  };

  loading.value = true;
  try {
    if (isEditing.value) {
      await turnoService.update(form.value.id, payload);
      Swal.fire('Actualizado', 'Turno modificado correctamente', 'success');
    } else {
      await turnoService.create(payload);
      Swal.fire('Guardado', 'Nuevo turno registrado', 'success');
    }
    await cargarTurnos();
    showModal.value = false;
  } catch (error) {
    Swal.fire('Error', error.response?.data?.detail || 'Error al guardar.', 'error');
  } finally {
    loading.value = false;
  }
};

// --- ACCIONES ---
const toggleStatus = async (turno) => {
  const nuevoEstado = turno.estado === 1 ? 0 : 1;
  try {
    await turnoService.toggleStatus(turno.id, { ...turno, estado: nuevoEstado });
    await cargarTurnos(); // Recargar para ver cambio visual
    const msg = nuevoEstado === 1 ? 'Activado' : 'Desactivado';
    Swal.fire('Estado Cambiado', `El turno ha sido ${msg}.`, 'success');
  } catch (error) {
    Swal.fire('Error', 'No se pudo cambiar el estado.', 'error');
  }
};

const eliminarTurno = async (id) => {
  const result = await Swal.fire({
    title: '¿Eliminar Turno?',
    text: "Esta acción es irreversible.",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    confirmButtonText: 'Sí, eliminar'
  });

  if (result.isConfirmed) {
    try {
      await turnoService.remove(id);
      turnos.value = turnos.value.filter(t => t.id !== id);
      Swal.fire('Eliminado', 'Turno eliminado.', 'success');
    } catch (error) {
      Swal.fire('Error', 'No se puede eliminar (quizás ya tenga horarios asignados).', 'error');
    }
  }
};

const formatTime = (t) => t ? t.substring(0, 5) : '';

// --- INICIALIZACIÓN ---
// Importante: Cargar apenas se monta la vista, sin esperar props
onMounted(() => {
  cargarTurnos();
});
</script>

<template>
  <div class="page-content">
    
    <div class="view-header">
      <div>
        <h2 class="title">Gestión de Turnos</h2>
        <p class="subtitle">Defina los horarios (Mañana, Tarde, Noche) para toda la escuela.</p>
      </div>
      <button @click="openModal()" class="btn-primary">
        <span class="icon">+</span> Nuevo Turno
      </button>
    </div>

    <div>
      <div v-if="loading && turnos.length === 0" class="loading-container">
        Cargando turnos...
      </div>

      <div v-else-if="turnos.length > 0" class="cards-grid">
        <div 
          v-for="turno in turnos" 
          :key="turno.id" 
          class="turno-card"
          :class="{'inactive': turno.estado === 0}"
        >
          <div class="card-header">
            <div class="icon-box">🕒</div>
            <div class="actions">
              <button @click="openModal(turno)" class="action-btn edit" title="Editar">✏️</button>
              <button @click="eliminarTurno(turno.id)" class="action-btn delete" title="Eliminar">🗑️</button>
            </div>
          </div>

          <div class="card-body">
            <h3 class="turno-name">{{ turno.nombre }}</h3>
            <div class="time-range">
              <span>{{ formatTime(turno.hora_inicio) }}</span>
              <span class="separator">➝</span>
              <span>{{ formatTime(turno.hora_fin) }}</span>
            </div>
          </div>

          <div class="card-footer">
            <span class="status-badge" :class="turno.estado === 1 ? 'active' : 'inactive'">
              {{ turno.estado === 1 ? 'Activo' : 'Inactivo' }}
            </span>
            <button @click="toggleStatus(turno)" class="toggle-link">
              {{ turno.estado === 1 ? 'Desactivar' : 'Activar' }}
            </button>
          </div>
        </div>
      </div>

      <div v-else class="no-data-state">
        <p>No hay turnos registrados en la escuela.</p>
        <button @click="openModal()" class="btn-link">Crear primer turno</button>
      </div>
    </div>

    <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
      <div class="modal-panel">
        <div class="modal-header">
          <h3>{{ isEditing ? 'Editar Turno' : 'Registrar Nuevo Turno' }}</h3>
          <button class="close-btn" @click="showModal = false">×</button>
        </div>
        
        <form @submit.prevent="saveTurno" class="modal-body">
          <div class="form-group">
            <label>Nombre del Turno</label>
            <input 
              v-model="form.nombre" 
              type="text" 
              placeholder="Ej. Mañana, Tarde" 
              required 
            />
          </div>

          <div class="grid-2">
            <div class="form-group">
              <label>Hora Inicio</label>
              <input v-model="form.hora_inicio" type="time" required />
            </div>
            <div class="form-group">
              <label>Hora Fin</label>
              <input v-model="form.hora_fin" type="time" required />
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="showModal = false">Cancelar</button>
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
/* Estilos Generales */
.page-content { padding: 2rem; max-width: 1200px; margin: 0 auto; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.title { font-size: 1.8rem; font-weight: 700; color: #1e293b; margin: 0; }
.subtitle { color: #64748b; margin-top: 0.5rem; }

/* Botones */
.btn-primary { background-color: #4f46e5; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; }
.btn-primary:hover { background-color: #4338ca; }
.btn-secondary { background: #e2e8f0; color: #475569; padding: 0.6rem 1.2rem; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; }
.btn-secondary:hover { background: #cbd5e1; }
.btn-link { background: none; border: none; color: #4f46e5; text-decoration: underline; cursor: pointer; margin-top: 1rem; }

/* Grid Cards */
.cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; }

.turno-card { background: white; border-radius: 12px; border: 1px solid #e2e8f0; padding: 1.25rem; transition: transform 0.2s, box-shadow 0.2s; display: flex; flex-direction: column; gap: 1rem; }
.turno-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
.turno-card.inactive { opacity: 0.75; background: #f8fafc; border-style: dashed; }

.card-header { display: flex; justify-content: space-between; align-items: flex-start; }
.icon-box { background: #e0e7ff; color: #4338ca; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
.actions { display: flex; gap: 0.5rem; }
.action-btn { background: none; border: none; cursor: pointer; font-size: 1.1rem; padding: 0.25rem; border-radius: 4px; }
.action-btn:hover { background: #f1f5f9; }
.action-btn.delete:hover { color: #ef4444; background: #fee2e2; }

.card-body { text-align: center; padding: 0.5rem 0; }
.turno-name { font-size: 1.25rem; font-weight: 700; color: #1e293b; margin: 0 0 0.5rem 0; }
.time-range { display: inline-flex; align-items: center; gap: 0.5rem; color: #64748b; font-weight: 500; background: #f1f5f9; padding: 0.25rem 1rem; border-radius: 99px; font-size: 0.9rem; }

.card-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 1rem; margin-top: auto; }
.toggle-link { background: none; border: none; font-size: 0.8rem; color: #64748b; cursor: pointer; text-decoration: underline; }

.status-badge { padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
.status-badge.active { background: #dcfce7; color: #166534; }
.status-badge.inactive { background: #fee2e2; color: #991b1b; }

.no-data-state { text-align: center; padding: 4rem; color: #94a3b8; border: 2px dashed #cbd5e1; border-radius: 12px; }
.loading-container { text-align: center; padding: 2rem; color: #64748b; }

/* Modal */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 50; }
.modal-panel { background: white; width: 100%; max-width: 450px; border-radius: 12px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); overflow: hidden; }
.modal-header { padding: 1.25rem; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { margin: 0; font-size: 1.1rem; color: #334155; font-weight: 700; }
.close-btn { background: none; border: none; font-size: 1.5rem; color: #94a3b8; cursor: pointer; }
.modal-body { padding: 1.5rem; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 0.4rem; }
.form-group input { width: 100%; padding: 0.6rem; border: 1px solid #cbd5e1; border-radius: 6px; outline: none; }
.form-group input:focus { border-color: #4f46e5; ring: 2px solid #e0e7ff; }
.modal-footer { display: flex; justify-content: flex-end; gap: 0.75rem; padding-top: 1rem; }
</style>