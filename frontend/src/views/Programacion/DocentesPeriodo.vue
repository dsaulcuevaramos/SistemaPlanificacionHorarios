<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Swal from 'sweetalert2';

// Servicios
import docenteService from '../../api/docenteService';
import contratoService from '../../api/contratoService';
import turnoService from '../../api/turnoService'; // [NUEVO] Importamos el servicio de turnos
import periodoService from '../../api/periodoService';

const route = useRoute();
const router = useRouter();
const idPeriodo = route.params.id;
const periodoActual = ref(null);

const periodosAnteriores = ref([]);
const idPeriodoAnteriorSel = ref(null);
const showRenovarModal = ref(false);

// --- ESTADO ---
const docentes = ref([]);
const disponibilidad = ref([]);
const listaTurnos = ref([]); // [NUEVO] Lista para almacenar los turnos de la BD
const loading = ref(true);
const saving = ref(false);
const searchTerm = ref('');
const showModal = ref(false);

// Formulario reactivo
const form = ref({
    id_docente: null,
    nombre_docente: '',
    id_periodo: parseInt(idPeriodo),
    fecha_inicio: '',
    fecha_fin: '',
    horas_tope_semanales: 20,
    turnos_preferidos: '' // Inicializamos vacío para obligar a seleccionar
});


// --- CARGA DE DATOS ---
const initData = async () => {
    loading.value = true;
    try {
        // 1. Cargamos Docentes, Disponibilidad y [NUEVO] Turnos en paralelo
        const [docsResp, dispResp, turnosResp] = await Promise.all([
            docenteService.getAll(),
            contratoService.getDisponibilidadByPeriodo(idPeriodo),
            turnoService.getAll() // Traemos los turnos de la escuela
        ]);

        docentes.value = docsResp;
        disponibilidad.value = dispResp;
        listaTurnos.value = turnosResp; // Guardamos los turnos

        try {
          const todosPeriodos = await periodoService.getAll();
          // Filtramos para que solo muestre periodos distintos al actual
          periodosAnteriores.value = todosPeriodos.filter(p => p.id != idPeriodo);
        } catch(e) { console.error(e); }

        // 2. Cargamos el periodo por separado (para no romper todo si falla)
        try {
            // Para ser fiel a tu código anterior:
            const { default: api } = await import('../../api/axios'); // Import dinámico o usar el import arriba si ya lo tienes
            const perRespAxios = await api.get(`/periodos/${idPeriodo}`);
            periodoActual.value = perRespAxios.data;
        } catch (perError) {
            console.error("Aviso: No se pudo cargar detalle del periodo", perError);
        }

    } catch (error) {
        console.error(error);
        Swal.fire('Error', 'No se pudo cargar la información inicial.', 'error');
    } finally {
        loading.value = false;
    }
};

onMounted(() => initData());

// --- LÓGICA DE FILTRADO ---
const docentesConEstado = computed(() => {
    return docentes.value.map(doc => {
        const asignacion = disponibilidad.value.find(d => d.id_docente === doc.id);
        return {
            ...doc,
            estaAsignado: !!asignacion,
            horasEnPeriodo: asignacion ? asignacion.horas_asignadas_actuales : 0
        };
    }).filter(doc => {
        const term = searchTerm.value.toLowerCase();
        return doc.nombre.toLowerCase().includes(term) || 
               doc.apellido.toLowerCase().includes(term) || 
               doc.dni.includes(term);
    });
});

// --- UTILIDADES ---
const formatTime = (t) => t ? t.substring(0, 5) : '';

// --- ACCIONES ---
const openContratarModal = (docente) => {
    form.value.id_docente = docente.id;
    form.value.nombre_docente = `${docente.apellido}, ${docente.nombre}`;
    form.value.horas_tope_semanales = docente.horas_maximas_semanales || 20;
    
    // Seleccionar el primer turno por defecto si existe, o dejar vacío
    if (listaTurnos.value.length > 0) {
        form.value.turnos_preferidos = listaTurnos.value[0].nombre;
    } else {
        form.value.turnos_preferidos = '';
    }

    showModal.value = true;
};


const handleRenovacionMasiva = async () => {
    if (!idPeriodoAnteriorSel.value) return Swal.fire('Error', 'Seleccione un periodo fuente', 'warning');
    
    loading.value = true;
    try {
        await contratoService.renovarMasivo({
            id_periodo_anterior: idPeriodoAnteriorSel.value,
            id_periodo_nuevo: parseInt(idPeriodo)
        });
        Swal.fire('Éxito', 'Docentes importados correctamente', 'success');
        showRenovarModal.value = false;
        await initData(); // Recargamos la tabla
    } catch (e) {
        Swal.fire('Error', 'Falló la renovación masiva', 'error');
    } finally {
        loading.value = false;
    }
};


const handleGuardarContrato = async () => {
    if (!form.value.turnos_preferidos) {
        Swal.fire('Atención', 'Debe seleccionar un turno preferido.', 'warning');
        return;
    }

    saving.value = true;
    try {
        const payload = {
            id_docente: form.value.id_docente,
            id_periodo: parseInt(idPeriodo),
            horas_tope_semanales: form.value.horas_tope_semanales,
            turnos_preferidos: form.value.turnos_preferidos // Enviamos el nombre del turno
        };

        await contratoService.asignarDocenteAPeriodo(payload);
        
        Swal.fire({
            title: '¡Éxito!',
            text: 'Docente habilitado para el periodo académico.',
            icon: 'success',
            confirmButtonColor: '#4f46e5'
        }); 

        showModal.value = false;
        await initData(); 
    } catch (error) {
        const msg = error.response?.data?.detail || 'No se pudo procesar el contrato.';
        Swal.fire('Error', msg, 'error');
    } finally {
        saving.value = false;
    }
};

const handleQuitarContrato = async (docente) => {
    const result = await Swal.fire({
        title: '¿Eliminar contrato?',
        text: `Se quitará a ${docente.nombre} de este periodo.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonColor: '#d33'
    });

    if (result.isConfirmed) {
        try {
            await contratoService.quitarContrato(idPeriodo, docente.id);
            Swal.fire('Eliminado', 'Contrato removido.', 'success');
            await initData();
        } catch (error) {
            Swal.fire('Error', 'No se pudo eliminar el contrato.', 'error');
        }
    }
};

const irAtras = () => router.back();
</script>

<template>
  <div class="page-content">
    
    <div class="view-header">
      <div class="flex items-center gap-4">
        <button @click="irAtras" class="btn-back">← Volver</button>
        <div>
          <h1 class="title">Contratación de Docentes</h1>
          <p class="subtitle">Asigne personal docente al periodo académico actual.</p>
        </div>
      </div>
    </div>

    <div class="toolbar">
      <div class="search-container">
        </div>
      
      <div class="actions-right">
          <button @click="showRenovarModal = true" class="btn-secondary">
              🔄 Traer del Ciclo Pasado
          </button>
          
          <div class="stats">
              <span class="pill">Total: {{ docentes.length }}</span>
              <span class="pill pill-success">Contratados: {{ disponibilidad.length }}</span>
          </div>
      </div>
    </div>


    <div v-if="showRenovarModal" class="modal-backdrop" @click.self="showRenovarModal = false">
      <div class="modal-panel small-modal">
          <div class="modal-header">
              <h3>Renovación Masiva</h3>
              <button class="close-btn" @click="showRenovarModal = false">&times;</button>
          </div>
          <div class="modal-body">
              <p style="margin-bottom:1rem; color:#64748b;">Seleccione el periodo del cual desea copiar la lista de docentes contratados:</p>
              <select v-model="idPeriodoAnteriorSel" class="full-width-select">
                  <option :value="null">-- Seleccionar Periodo Anterior --</option>
                  <option v-for="p in periodosAnteriores" :key="p.id" :value="p.id">{{ p.codigo || p.nombre }}</option>
              </select>
          </div>
          <div class="modal-footer">
              <button @click="handleRenovacionMasiva" class="btn-primary-modal">
                  Importar Docentes
              </button>
          </div>
      </div>
    </div>


    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Docente</th>
            <th>DNI / Tipo</th>
            <th>Estado en Periodo</th>
            <th class="text-center">Carga Actual</th>
            <th class="text-right">Acción</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="5" class="text-center py-8">Cargando datos...</td>
          </tr>
          <tr v-else v-for="doc in docentesConEstado" :key="doc.id" :class="{'row-assigned': doc.estaAsignado}">
            <td>
              <div class="user-cell">
                <div class="avatar-circle">{{ doc.nombre[0] }}{{ doc.apellido[0] }}</div>
                <div class="user-info">
                  <span class="font-bold">{{ doc.apellido }}, {{ doc.nombre }}</span>
                  <span class="text-xs text-gray-500">{{ doc.email }}</span>
                </div>
              </div>
            </td>
            <td>
              <div class="flex flex-col">
                <span class="text-sm">🆔 {{ doc.dni }}</span>
                <span class="badge-type">{{ doc.tipo_docente }}</span>
              </div>
            </td>
            <td>
              <span v-if="doc.estaAsignado" class="status-badge success">✓ Contratado</span>
              <span v-else class="status-badge warning">○ Pendiente</span>
            </td>
            <td class="text-center font-bold">
              {{ doc.horasEnPeriodo }}h
            </td>
            <td class="text-right">
              <div class="flex justify-end gap-2">
                <button 
                  v-if="!doc.estaAsignado" 
                  @click="openContratarModal(doc)" 
                  class="btn-primary-sm"
                >
                  Contratar
                </button>
                <template v-else>
                  <button class="btn-icon-view" title="Ver Ficha">📄</button>
                  <button @click="handleQuitarContrato(doc)" class="btn-icon-delete" title="Quitar Contrato">🗑️</button>
                </template>
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
            <h3 class="text-lg font-bold text-slate-800">Asignación al Periodo</h3>
            <span class="text-xs text-slate-500">Configuración de contrato</span>
          </div>
          <button class="close-btn" @click="showModal = false">&times;</button>
        </div>
        
        <form @submit.prevent="handleGuardarContrato" class="modal-body">
          
          <div class="docente-banner">
            <p class="label">Docente a contratar:</p>
            <h4 class="name">{{ form.nombre_docente }}</h4>
          </div>

          <div class="periodo-info">
            <div class="info-item">
              <p class="label">Fecha Inicio</p>
              <p class="value">{{ periodoActual?.fecha_inicio || 'Adaptado del periodo' }}</p>
            </div>
            <div class="divider"></div>
            <div class="info-item">
              <p class="label">Fecha Fin</p>
              <p class="value">{{ periodoActual?.fecha_fin || 'Adaptado del periodo' }}</p>
            </div>
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label>Tope Horas Semanale*</label>
              <input 
                v-model.number="form.horas_tope_semanales" 
                type="number" 
                min="1" max="40" 
                placeholder="Ej. 20"
                required 
              />
              <small>Máximo permitido por contrato</small>
            </div>
            
            <div class="form-group">
              <label>Preferencia de Turno*</label>
              <select v-model="form.turnos_preferidos" required>
                <option value="" disabled>-- Seleccione --</option>
                <option 
                  v-for="turno in listaTurnos" 
                  :key="turno.id" 
                  :value="turno.nombre"
                >
                  {{ turno.nombre }} ({{ formatTime(turno.hora_inicio) }} - {{ formatTime(turno.hora_fin) }})
                </option>
              </select>
              <small>Basado en turnos de la escuela</small>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="showModal = false">
              Cancelar
            </button>
            <button type="submit" class="btn-primary-modal" :disabled="saving">
              {{ saving ? 'Procesando...' : 'Confirmar Contrato' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* --- ESTRUCTURA DE PÁGINA --- */
.page-content { padding: 2rem; max-width: 1400px; margin: 0 auto; }
.view-header { margin-bottom: 2rem; }
.title { font-size: 1.8rem; font-weight: 700; color: #1e293b; margin: 0; }
.subtitle { color: #64748b; margin-top: 0.5rem; }

/* --- TOOLBAR & TABLA --- */
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; gap: 1rem; }
.search-container { flex: 1; position: relative; max-width: 400px; }
.search-input { width: 100%; padding: 0.75rem 1rem 0.75rem 2.8rem; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 0.95rem; outline: none; transition: border-color 0.2s; }
.search-input:focus { border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1); }
.search-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: #94a3b8; }

.stats { display: flex; gap: 0.8rem; }
.pill { padding: 0.4rem 1rem; background: #f1f5f9; border-radius: 99px; font-size: 0.85rem; font-weight: 600; color: #475569; }
.pill-success { background: #dcfce7; color: #166534; }

.table-container { background: white; border-radius: 16px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #f8fafc; padding: 1rem 1.5rem; text-align: left; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #64748b; border-bottom: 1px solid #e2e8f0; }
.data-table td { padding: 1.25rem 1.5rem; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
.data-table tr:last-child td { border-bottom: none; }
.row-assigned { background-color: #f0fdf4; }

/* --- CELDAS Y BADGES --- */
.user-cell { display: flex; align-items: center; gap: 1rem; }
.avatar-circle { width: 40px; height: 40px; background: #e0e7ff; color: #4338ca; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.9rem; }
.user-info { display: flex; flex-direction: column; }
.user-info .font-bold { color: #1e293b; }
.badge-type { background: #f1f5f9; padding: 4px 8px; border-radius: 6px; font-size: 0.7rem; color: #475569; font-weight: 700; text-transform: uppercase; border: 1px solid #e2e8f0; }

.status-badge { padding: 0.35rem 0.75rem; border-radius: 99px; font-size: 0.75rem; font-weight: 700; display: inline-flex; align-items: center; gap: 0.4rem; }
.status-badge.success { background: #dcfce7; color: #166534; }
.status-badge.warning { background: #fff7ed; color: #c2410c; border: 1px solid #ffedd5; }

/* --- BOTONES --- */
.btn-back { background: none; border: 1px solid #e2e8f0; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; color: #64748b; font-weight: 600; transition: all 0.2s; }
.btn-back:hover { background: #f8fafc; color: #1e293b; border-color: #cbd5e1; }

.btn-primary-sm { background: #4f46e5; color: white; padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.85rem; font-weight: 600; border: none; cursor: pointer; transition: background 0.2s; box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2); }
.btn-primary-sm:hover { background: #4338ca; transform: translateY(-1px); }

.btn-icon-view, .btn-icon-delete { background: none; border: none; cursor: pointer; font-size: 1.2rem; padding: 0.4rem; border-radius: 6px; transition: background 0.2s; }
.btn-icon-view:hover { background: #f1f5f9; }
.btn-icon-delete:hover { background: #fee2e2; color: #dc2626; }

/* --- MODAL (ESTILOS ARREGLADOS) --- */
.modal-backdrop { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 50; }
.modal-panel { background: white; width: 100%; max-width: 500px; border-radius: 16px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); overflow: hidden; animation: modalSlideUp 0.3s ease-out; }

.modal-header { padding: 1.5rem; background: #ffffff; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: start; }
.close-btn { background: none; border: none; font-size: 1.8rem; line-height: 1; color: #94a3b8; cursor: pointer; padding: 0 0.5rem; }
.close-btn:hover { color: #475569; }

.modal-body { padding: 1.5rem; }

/* Banner Docente */
.docente-banner { background: #e0e7ff; border-left: 4px solid #4f46e5; padding: 1rem; border-radius: 0 8px 8px 0; margin-bottom: 1.5rem; }
.docente-banner .label { font-size: 0.75rem; color: #4338ca; font-weight: 600; margin-bottom: 0.2rem; }
.docente-banner .name { font-size: 1.1rem; color: #312e81; font-weight: 700; margin: 0; }

/* Info Periodo */
.periodo-info { display: flex; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem; }
.info-item { flex: 1; text-align: center; }
.info-item .label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; font-weight: 700; margin-bottom: 0.25rem; }
.info-item .value { font-size: 0.95rem; font-weight: 600; color: #334155; }
.divider { width: 1px; height: 30px; background: #cbd5e1; margin: 0 1rem; }

/* Formularios - Aquí estaba el problema de "marcos cortos" */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }
.form-group { display: flex; flex-direction: column; } /* Vertical stacking */
.form-group label { font-size: 0.9rem; font-weight: 600; color: #334155; margin-bottom: 0.5rem; }
.form-group input, .form-group select { 
  width: 100%; /* Ocupa todo el espacio */
  padding: 0.75rem; 
  border: 1px solid #cbd5e1; 
  border-radius: 8px; 
  font-size: 0.95rem; 
  outline: none; 
  transition: all 0.2s;
  background-color: white;
}
.form-group input:focus, .form-group select:focus { border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1); }
.form-group small { display: block; margin-top: 0.4rem; font-size: 0.75rem; color: #94a3b8; }

.modal-footer { display: flex; justify-content: flex-end; gap: 1rem; padding-top: 1.5rem; border-top: 1px solid #f1f5f9; margin-top: 0.5rem; }
.btn-secondary { background: #f1f5f9; color: #475569; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; border: none; cursor: pointer; transition: background 0.2s; }
.btn-secondary:hover { background: #e2e8f0; }
.btn-primary-modal { background: #4f46e5; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; border: none; cursor: pointer; transition: background 0.2s; box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.3); }
.btn-primary-modal:hover { background: #4338ca; transform: translateY(-1px); }

@keyframes modalSlideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.actions-right {
    display: flex;
    align-items: center;
    gap: 1rem;
}
.full-width-select {
    width: 100%;
    padding: 10px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 1rem;
}
.small-modal {
    max-width: 400px !important;
}
</style>