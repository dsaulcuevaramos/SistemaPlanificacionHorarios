<script setup>
import { ref, onMounted, watch } from 'vue';
import bloqueService from '../../api/bloqueService';
import turnoService from '../../api/turnoService';
import Swal from 'sweetalert2';

// --- ESTADO ---
const turnos = ref([]);
const idTurnoSeleccionado = ref(null);
const bloques = ref([]);
const loading = ref(false);
const showModal = ref(false);

const form = ref({
  dia_semana: 'Lunes', 
  hora_inicio: '',
  hora_fin: '',
  orden: 1,
  id_turno: null
});

// --- CARGA ---
const cargarDatosIniciales = async () => {
  try {
    turnos.value = await turnoService.getAll();
    if (turnos.value.length > 0) {
      idTurnoSeleccionado.value = turnos.value[0].id;
    }
  } catch (error) {
    Swal.fire('Error', 'No se pudieron cargar los turnos.', 'error');
  }
};

const cargarBloques = async () => {
  if (!idTurnoSeleccionado.value) return;
  loading.value = true;
  try {
    bloques.value = await bloqueService.getByTurno(idTurnoSeleccionado.value);
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// --- ACCIONES ---
const handleGuardarBloque = async () => {
  form.value.id_turno = idTurnoSeleccionado.value;
  try {
    await bloqueService.create(form.value);
    Swal.fire('Éxito', 'Bloque horario creado', 'success');
    showModal.value = false;
    cargarBloques();
  } catch (error) {
    Swal.fire('Error', 'No se pudo guardar el bloque.', 'error');
  }
};

const eliminarBloque = async (id) => {
  const res = await Swal.fire({
    title: '¿Eliminar bloque?',
    text: "Esta acción no se puede deshacer.",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    confirmButtonText: 'Sí, eliminar'
  });
  if (res.isConfirmed) {
    try {
      await bloqueService.remove(id);
      cargarBloques();
      Swal.fire('Eliminado', 'El bloque ha sido removido.', 'success');
    } catch (error) {
      Swal.fire('Error', 'No se pudo eliminar.', 'error');
    }
  }
};

watch(idTurnoSeleccionado, () => cargarBloques());
onMounted(() => cargarDatosIniciales());
</script>

<template>
  <div class="page-content">
    
    <div class="view-header">
      <div>
        <h2 class="title">Configuración de Bloques Horarios</h2>
        <p class="subtitle">Estructure el tiempo de los turnos para la programación de clases.</p>
      </div>
    </div>

    <div class="toolbar-card">
      <div class="selector-group">
        <label>Seleccionar Turno Académico:</label>
        <select v-model="idTurnoSeleccionado" class="custom-select">
          <option v-for="t in turnos" :key="t.id" :value="t.id">{{ t.nombre }}</option>
        </select>
      </div>
      <button @click="showModal = true" class="btn-primary" :disabled="!idTurnoSeleccionado">
        <span class="icon">+</span> Agregar Nuevo Bloque
      </button>
    </div>

    <div class="table-container shadow-sm">
      <table class="data-table">
        <thead>
          <tr>
            <th class="w-20">Orden</th>
            <th>Día de la Semana</th>
            <th>Hora Inicio</th>
            <th>Hora Fin</th>
            <th class="text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="5" class="text-center py-10 text-slate-500">Cargando bloques...</td>
          </tr>
          <tr v-else v-for="b in bloques" :key="b.id" class="hover:bg-slate-50">
            <td class="font-bold text-indigo-600 text-center">
               <span class="order-badge">#{{ b.orden }}</span>
            </td>
            <td class="font-medium text-slate-700">{{ b.dia_semana }}</td>
            <td>
              <div class="time-tag inicio">{{ b.hora_inicio.substring(0,5) }}</div>
            </td>
            <td>
              <div class="time-tag fin">{{ b.hora_fin.substring(0,5) }}</div>
            </td>
            <td class="text-right">
              <button @click="eliminarBloque(b.id)" class="btn-icon-delete" title="Eliminar bloque">
                🗑️
              </button>
            </td>
          </tr>
          <tr v-if="!loading && bloques.length === 0">
            <td colspan="5" class="empty-state">
              <div class="py-12">
                <p class="text-slate-400">No hay bloques configurados para este turno.</p>
                <small class="text-slate-300">Haga clic en "+ Agregar Bloque" para comenzar.</small>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
      <div class="modal-panel shadow-2xl">
        <div class="modal-header">
          <div class="flex flex-col">
            <h3 class="text-lg font-bold text-slate-800">Registrar Bloque</h3>
            <span class="text-xs text-slate-500">Defina un nuevo intervalo de tiempo</span>
          </div>
          <button class="close-btn" @click="showModal = false">&times;</button>
        </div>
        
        <form @submit.prevent="handleGuardarBloque" class="modal-body">
          <div class="form-group">
            <label>Día de la Semana</label>
            <select v-model="form.dia_semana" class="w-full" required>
              <option>Lunes</option>
              <option>Martes</option>
              <option>Miércoles</option>
              <option>Jueves</option>
              <option>Viernes</option>
              <option>Sábado</option>
              <option>Domingo</option>
            </select>
          </div>

          <div class="grid-2 gap-4">
            <div class="form-group">
              <label>Hora Inicio</label>
              <input type="time" v-model="form.hora_inicio" class="w-full" required />
            </div>
            <div class="form-group">
              <label>Hora Fin</label>
              <input type="time" v-model="form.hora_fin" class="w-full" required />
            </div>
          </div>

          <div class="form-group">
            <label>Número de Orden</label>
            <input type="number" v-model="form.orden" min="1" class="w-full" required />
            <small class="text-slate-400 text-[10px]">Define la posición secuencial en el horario.</small>
          </div>

          <div class="modal-footer mt-6">
            <button type="button" class="btn-secondary" @click="showModal = false">Cancelar</button>
            <button type="submit" class="btn-primary-modal">Guardar Bloque</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-content { padding: 2rem; max-width: 1100px; margin: 0 auto; }

/* Header */
.view-header { margin-bottom: 2rem; }
.title { font-size: 1.8rem; font-weight: 800; color: #1e293b; margin: 0; }
.subtitle { color: #64748b; font-size: 0.95rem; }

/* Toolbar */
.toolbar-card {
  background: white;
  padding: 1.25rem 1.5rem;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.selector-group { display: flex; align-items: center; gap: 1rem; }
.selector-group label { font-size: 0.9rem; font-weight: 700; color: #475569; }

.custom-select {
  padding: 0.6rem 1rem;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background-color: #f8fafc;
  min-width: 200px;
  outline: none;
}

.btn-primary {
  background: #4f46e5;
  color: white;
  padding: 0.7rem 1.2rem;
  border-radius: 8px;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-primary:hover:not(:disabled) { background: #4338ca; transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

/* Tabla */
.table-container { background: white; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #f8fafc; padding: 1rem; text-align: left; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; border-bottom: 1px solid #e2e8f0; }
.data-table td { padding: 1rem; border-bottom: 1px solid #f1f5f9; color: #475569; }

.order-badge {
  background: #eef2ff;
  color: #4338ca;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  font-size: 0.85rem;
}

.time-tag {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-family: monospace;
  font-weight: 600;
  font-size: 0.9rem;
}
.time-tag.inicio { background: #ecfdf5; color: #059669; }
.time-tag.fin { background: #fff1f2; color: #e11d48; }

.btn-icon-delete {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.4rem;
  border-radius: 6px;
  transition: background 0.2s;
}
.btn-icon-delete:hover { background: #fee2e2; }

.empty-state { text-align: center; }

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal-panel { background: white; width: 100%; max-width: 450px; border-radius: 16px; overflow: hidden; }

.modal-header {
  padding: 1.25rem 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn { background: none; border: none; font-size: 1.8rem; color: #94a3b8; cursor: pointer; }

.modal-body { padding: 1.5rem; }

.form-group { margin-bottom: 1.25rem; display: flex; flex-direction: column; }
.form-group label { font-size: 0.85rem; font-weight: 700; color: #475569; margin-bottom: 0.5rem; }
.form-group input, .form-group select {
  padding: 0.65rem 0.8rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s;
}
.form-group input:focus, .form-group select:focus { border-color: #4f46e5; ring: 2px solid #e0e7ff; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }

.modal-footer { display: flex; justify-content: flex-end; gap: 0.75rem; border-top: 1px solid #f1f5f9; padding-top: 1.25rem; }

.btn-secondary { background: #f1f5f9; color: #475569; padding: 0.65rem 1.2rem; border-radius: 8px; font-weight: 700; border: none; cursor: pointer; }
.btn-primary-modal { background: #4f46e5; color: white; padding: 0.65rem 1.2rem; border-radius: 8px; font-weight: 700; border: none; cursor: pointer; flex: 1; }

@keyframes slideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>