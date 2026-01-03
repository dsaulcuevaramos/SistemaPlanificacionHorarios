<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import bloqueService from '../../api/bloqueService';
import turnoService from '../../api/turnoService';
import Swal from 'sweetalert2';

// --- ESTADO ---
const turnos = ref([]);
const idTurnoSeleccionado = ref(null);
const loading = ref(false);
const diasSemana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
const diasSeleccionados = ref(['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']);

// Esta es la lista que se sincronizará con la DB
const intervalos = ref([]); 

const turnoActual = computed(() => {
    return turnos.value.find(t => t.id === idTurnoSeleccionado.value);
});

// --- CARGA DE DATOS ---
const cargarTurnos = async () => {
    try {
        turnos.value = await turnoService.getAll();
        if (turnos.value.length > 0) idTurnoSeleccionado.value = turnos.value[0].id;
    } catch (e) {
        Swal.fire('Error', 'No se cargaron los turnos', 'error');
    }
};


const timeToMinutes = (timeStr) => {
    if (!timeStr) return 0;
    const [hrs, mins] = timeStr.split(':').map(Number);
    return (hrs * 60) + mins;
};

const validarEstructuraCompleta = () => {
    if (!turnoActual.value) return false;

    // Límites del turno convertidos a minutos
    const limiteInicio = timeToMinutes(turnoActual.value.hora_inicio);
    const limiteFin = timeToMinutes(turnoActual.value.hora_fin);

    for (const inv of intervalos.value) {
        const invInicio = timeToMinutes(inv.inicio);
        const invFin = timeToMinutes(inv.fin);

        // 1. Validar que el inicio no sea antes del turno
        if (invInicio < limiteInicio) {
            Swal.fire('Error', `El bloque de las ${inv.inicio} empieza antes que el turno (${turnoActual.value.hora_inicio.substring(0,5)})`, 'error');
            return false;
        }

        // 2. Validar que el fin no sea después del turno
        if (invFin > limiteFin) {
            Swal.fire('Error', `El bloque de las ${inv.fin} termina después que el turno (${turnoActual.value.hora_fin.substring(0,5)})`, 'error');
            return false;
        }

        // 3. Validar consistencia interna del bloque
        if (invInicio >= invFin) {
            Swal.fire('Error', `El bloque con orden ${inv.orden} tiene una hora de fin inválida.`, 'error');
            return false;
        }
    }
    return true;
};



const cargarIntervalosDesdeDB = async () => {
    if (!idTurnoSeleccionado.value) return;
    loading.value = true;
    try {
        const bloquesDB = await bloqueService.getByTurno(idTurnoSeleccionado.value);
        
        if (bloquesDB.length > 0) {
            // Extraemos los bloques de un solo día (ej. Lunes) para usarlos como plantilla
            const mapaDias = { "Lunes": 1, "Martes": 2, "Miércoles": 3, "Jueves": 4, "Viernes": 5, "Sábado": 6, "Domingo": 7 };
            const ordenados = bloquesDB.sort((a, b) => {
                if (mapaDias[a.dia_semana] !== mapaDias[b.dia_semana]) {
                    return mapaDias[a.dia_semana] - mapaDias[b.dia_semana];
                }
                return a.orden - b.orden;
            });

            const primerDia = bloquesDB[0].dia_semana;
            intervalos.value = bloquesDB
                .filter(b => b.dia_semana === primerDia)
                .map(b => ({
                    inicio: b.hora_inicio.substring(0, 5),
                    fin: b.hora_fin.substring(0, 5),
                    orden: b.orden
                }))
                .sort((a, b) => a.orden - b.orden);
        } else {
            intervalos.value = []; // Si no hay datos, tabla vacía
        }
    } catch (error) {
        console.error("Error al cargar intervalos:", error);
    } finally {
        loading.value = false;
    }
};

// --- ACCIONES ---
const agregarFila = () => {
    const nuevoOrden = intervalos.value.length > 0 
        ? Math.max(...intervalos.value.map(i => i.orden)) + 1 
        : 1;
    intervalos.value.push({ inicio: '', fin: '', orden: nuevoOrden });
};

const limpiarRejillaTotal = async () => {
    const res = await Swal.fire({
        title: '¿Vaciar rejilla en la DB?',
        text: "Se borrarán permanentemente todos los bloques de este turno.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        confirmButtonText: 'Sí, borrar todo'
    });

    if (res.isConfirmed) {
        try {
            await bloqueService.removeAllByTurno(idTurnoSeleccionado.value);
            intervalos.value = [];
            Swal.fire('Eliminado', 'La base de datos se ha limpiado para este turno.', 'success');
        } catch (e) {
            Swal.fire('Error', 'No se pudo limpiar la base de datos.', 'error');
        }
    }
};

const generarBloques = async () => {
    if (diasSeleccionados.value.length === 0) {
        return Swal.fire('Atención', 'Selecciona al menos un día', 'warning');
    }
    
    // INTEGRACIÓN DE LA VALIDACIÓN
    if (!validarEstructuraCompleta()) return;
    
    loading.value = true;
    try {
        await bloqueService.removeAllByTurno(idTurnoSeleccionado.value);
        const payload = {
            id_turno: idTurnoSeleccionado.value,
            dias: diasSeleccionados.value,
            intervalos: intervalos.value
        };
        await bloqueService.createMasivo(payload);
        Swal.fire('Éxito', 'Rejilla generada y validada.', 'success');
        await cargarIntervalosDesdeDB();
    } catch (error) {
        Swal.fire('Error', 'Error al sincronizar.', 'error');
    } finally {
        loading.value = false;
    }
};

watch(idTurnoSeleccionado, () => cargarIntervalosDesdeDB());
onMounted(() => cargarTurnos());
</script>

<template>
  <div class="page-content">
    <div v-if="turnoActual" class="info-banner shadow-sm">
        <div class="flex justify-between items-center">
            <div class="flex items-center gap-3">
                <span class="icon-clock">🕒</span>
                <div>
                    <p class="text-xs uppercase font-bold text-indigo-500">Límites del Turno: {{ turnoActual.nombre }}</p>
                    <p class="text-lg font-black text-slate-700">
                        {{ turnoActual.hora_inicio.substring(0,5) }} — {{ turnoActual.hora_fin.substring(0,5) }}
                    </p>
                </div>
            </div>
            <button @click="limpiarRejillaTotal" class="btn-danger-outline">
                🗑️ Vaciar Datos en DB
            </button>
        </div>
    </div>

    <div class="grid-layout">
      <div class="config-card card">
        <div class="card-header-accent">1. Configuración de Turno</div>
        <div class="p-6">
          <div class="form-group mb-6">
            <label>Turno Seleccionado</label>
            <select v-model="idTurnoSeleccionado" class="custom-select w-full">
              <option v-for="t in turnos" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="mb-3 block">Días a replicar</label>
            <div class="days-grid">
              <label v-for="dia in diasSemana" :key="dia" class="day-chip">
                <input type="checkbox" :value="dia" v-model="diasSeleccionados">
                <span>{{ dia }}</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <div class="intervals-card card shadow-lg">
        <div class="card-header-accent flex justify-between items-center bg-indigo-50">
          <span>2. Estructura de Bloques ({{ intervalos.length }})</span>
          <button @click="agregarFila" class="btn-add-mini">+ Añadir Intervalo</button>
        </div>
        
        <div class="p-6">
          <table class="template-table">
            <thead>
              <tr>
                <th class="w-16">Orden</th>
                <th>Inicio</th>
                <th>Fin</th>
                <th class="w-10"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in intervalos" :key="index">
                <td><input type="number" v-model="item.orden" class="small-input text-center font-bold"></td>
                <td><input type="time" v-model="item.inicio" class="small-input"></td>
                <td><input type="time" v-model="item.fin" class="small-input"></td>
                <td class="text-right">
                  <button @click="intervalos.splice(index, 1)" class="text-red-400 hover:text-red-600">✕</button>
                </td>
              </tr>
              <tr v-if="intervalos.length === 0">
                <td colspan="4" class="py-20 text-center">
                    <p class="text-slate-400 italic">No hay bloques configurados para este turno.</p>
                    <button @click="agregarFila" class="text-indigo-600 font-bold underline mt-2">
                        Haz clic aquí para crear el primer bloque
                    </button>
                </td>
              </tr>
            </tbody>
          </table>

          <div class="mt-8 border-t pt-6" v-if="intervalos.length > 0">
            <button @click="generarBloques" class="btn-generate" :disabled="loading">
              {{ loading ? 'Sincronizando...' : '💾 Sincronizar y Guardar Horario' }}
            </button>
            <p class="text-[10px] text-center text-slate-400 mt-2">
                * Esto actualizará los bloques de todos los días seleccionados basándose en esta lista.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>


 .info-banner {
    background: #eef2ff;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid #c7d2fe;
} 

.page-content { padding: 2rem; max-width: 1200px; margin: 0 auto; }
.title { font-size: 1.8rem; font-weight: 800; color: #1e293b; }
.grid-layout { display: grid; grid-template-columns: 1fr 2fr; gap: 2rem; margin-top: 2rem; }

.card { background: white; border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0; }
.card-header-accent { background: #f8fafc; padding: 1rem 1.5rem; font-weight: 700; color: #475569; border-bottom: 1px solid #e2e8f0; }

.days-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }
.day-chip { 
    display: flex; align-items: center; gap: 0.5rem; padding: 0.6rem; 
    background: #f1f5f9; border-radius: 10px; cursor: pointer; transition: 0.2s;
}
.day-chip:has(input:checked) { background: #e0e7ff; color: #4338ca; font-weight: 600; }

.template-table { width: 100%; border-collapse: collapse; }
.template-table th { text-align: left; font-size: 0.75rem; color: #94a3b8; padding-bottom: 0.75rem; }
.template-table td { padding: 0.5rem 0; }

.small-input { width: 85%; padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 8px; outline: none; transition: 0.2s;}
.small-input:focus { border-color: #4f46e5; outline: none; background: #f5f3ff; }
.btn-add-mini { font-size: 0.75rem; background: #4f46e5; color: white; padding: 0.4rem 0.8rem; border-radius: 6px; }

.btn-generate { 
    background: #4f46e5; color: white; padding: 1rem 2rem; border-radius: 12px; 
    font-weight: 800; width: 100%; box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
}
.btn-generate:hover { background: #4338ca; transform: translateY(-2px); }
.btn-generate:disabled { background: #94a3b8; }

.btn-danger-mini {
    font-size: 0.75rem;
    background: #fee2e2;
    color: #b91c1c;
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    border: 1px solid #fecaca;
    font-weight: 600;
}
.btn-danger-mini:hover { background: #fecaca; }


.info-banner { background: white; border: 1px solid #e2e8f0; border-left: 5px solid #4f46e5; padding: 1rem 1.5rem; margin-bottom: 2rem; border-radius: 12px; }
.btn-danger-outline { padding: 0.5rem 1rem; border: 1px solid #fee2e2; background: #fff; color: #ef4444; border-radius: 8px; font-size: 0.8rem; font-weight: 600; cursor: pointer; }
.btn-danger-outline:hover { background: #fee2e2; }

</style>