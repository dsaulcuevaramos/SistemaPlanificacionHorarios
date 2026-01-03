<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Swal from 'sweetalert2';

// Servicios
import grupoService from '../../api/grupoService';
import contratoService from '../../api/contratoService'; 
import turnoService from '../../api/turnoService';       
import docenteService from '../../api/docenteService';

const route = useRoute();
const router = useRouter();
const idPeriodo = route.params.id;

// Datos
const cursosList = ref([]);
const docentesContratados = ref([]);
const listaDocentes = ref([]);
const turnos = ref([]);
const loading = ref(true);

// Modal
const showModal = ref(false);
const cursoSeleccionado = ref(null);
const docenteSeleccionado = ref(null);
const form = ref({
    cantidad_grupos: 1,
    id_docente: null,
    id_turno: null,
    vacantes_por_grupo: 40
});


const isEditing = ref(false);
const currentGroupId = ref(null);

// --- NUEVO: Propiedad Computada para Agrupar por Ciclo ---
const cursosPorCiclo = computed(() => {
    // 1. Agrupar
    const grupos = {};
    cursosList.value.forEach(item => {
        // Aseguramos que exista la propiedad ciclo, si no, lo mandamos a 'Otros'
        const ciclo = item.curso?.ciclo || 'Sin Ciclo'; 
        if (!grupos[ciclo]) {
            grupos[ciclo] = [];
        }
        grupos[ciclo].push(item);
    });

    // 2. Ordenar las llaves (los ciclos) numéricamente
    const ciclosOrdenados = Object.keys(grupos).sort((a, b) => {
        // Intenta convertir a número para ordenar correctamente (1, 2, 10 en vez de 1, 10, 2)
        return parseInt(a) - parseInt(b);
    });

    // 3. Retornar objeto ordenado para iterar
    return ciclosOrdenados.map(ciclo => ({
        titulo: ciclo,
        cursos: grupos[ciclo]
    }));
});

// Carga Inicial
const initData = async () => {
    loading.value = true;
    try {
        // 1. Descargar todo
        const [cursosResp, docentesResp, turnosResp, todosLosDocentesResp] = await Promise.all([
            grupoService.getCursosConGrupos(idPeriodo),
            contratoService.getDisponibilidadByPeriodo(idPeriodo),
            turnoService.getAll(),
            docenteService.getAll()
        ]);
        
        // 2. Limpiar la data
        const arrayDisponibilidad = docentesResp.data || docentesResp || []; 
        const arrayNombres = todosLosDocentesResp.data || todosLosDocentesResp || [];
        // Guardamos los cursos temporalmente
        let cursosTemp = cursosResp.data || cursosResp || [];

        // 3. LOGICA MAGICA: Inyectar el docente dentro de cada grupo para que se vea en la tarjeta
        cursosTemp.forEach(curso => {
            if (curso.grupos) {
                curso.grupos.forEach(grupo => {
                    // Buscamos al dueño del id_docente en la lista de nombres
                    const profe = arrayNombres.find(d => d.id === grupo.id_docente);
                    if (profe) {
                        // Le creamos la propiedad 'docente' al grupo para que el HTML la lea
                        grupo.docente = {
                            ...profe,
                            // Creamos nombre_completo por si tu HTML lo pide así
                            nombre_completo: `${profe.nombre} ${profe.apellido}` 
                        };
                    }
                });
            }
        });

        // 4. Asignar a la vista
        cursosList.value = cursosTemp; // Ahora los grupos ya tienen nombre de docente

        // 5. Preparar el Select del Modal (Cruce de disponibilidad)
        const listaCruzada = arrayDisponibilidad.map(dispo => {
            const infoDocente = arrayNombres.find(d => d.id === dispo.id_docente);
            return {
                ...dispo,
                nombre: infoDocente ? infoDocente.nombre : 'Docente',
                apellido: infoDocente ? infoDocente.apellido : 'Desconocido'
            };
        });
        listaDocentes.value = listaCruzada;

        turnos.value = turnosResp.data || turnosResp || [];
     
    } catch (e) {
        console.error(e);
        Swal.fire('Error', 'No se pudo cargar la información.', 'error');
    } finally {
        loading.value = false;
    }
};

onMounted(() => initData());


const editarGrupo = (grupo, cursoPadre) => {
    isEditing.value = true;
    currentGroupId.value = grupo.id;
    cursoSeleccionado.value = cursoPadre; // Necesario para mostrar el título
    
    // Rellenamos el formulario con los datos actuales del grupo
    form.value = {
        cantidad_grupos: 1, // En edición esto no se usa o se bloquea
        id_docente: grupo.id_docente || "", // Asigna el docente actual si tiene
        id_turno: grupo.id_turno,
        vacantes_por_grupo: grupo.vacantes
    };
    showModal.value = true;
};

// Acciones
const abrirModal = (curso) => {
    isEditing.value = false;
    currentGroupId.value = null;
    cursoSeleccionado.value = curso;
    form.value = {
        cantidad_grupos: 1,
        id_docente: null, // Resetear docente
        id_turno: turnos.value[0]?.id || null,
        vacantes_por_grupo: 40
    };
    showModal.value = true; 
};  


const guardarGrupos = async () => {
    // Validaciones básicas
    if (!form.value.id_turno) return Swal.fire('Atención', 'Seleccione un turno', 'warning');
    if (form.value.vacantes_por_grupo < 1) return Swal.fire('Error', 'Las vacantes deben ser mayores a 0', 'warning');

    try {
        if (isEditing.value) {
            // ===============================================
            // MODO EDICIÓN (UPDATE)
            // ===============================================
            // AQUÍ ESTABA EL ERROR: No uses crearLote, usa update/editar
            await grupoService.update(currentGroupId.value, {
                id_docente: form.value.id_docente,
                id_turno: form.value.id_turno,
                vacantes: form.value.vacantes_por_grupo
                // Nota: Al editar no mandamos cantidad_grupos ni id_curso
            });
            
            Swal.fire({ title: 'Éxito', text: 'Grupo actualizado', icon: 'success', timer: 1500, showConfirmButton: false });

        } else {
            // ===============================================
            // MODO CREACIÓN (CREATE)
            // ===============================================
            if (form.value.cantidad_grupos < 1) return Swal.fire('Error', 'Debe crear al menos 1 grupo', 'warning');

            await grupoService.crearLote({
                id_curso_aperturado: cursoSeleccionado.value.id,
                ...form.value 
            });
            
            Swal.fire('Éxito', 'Grupos creados', 'success');
        }

        showModal.value = false;
        await initData(); // Recargamos para ver los cambios

    } catch (e) {
        console.error(e);
        // EXTRAER EL MENSAJE DETALLADO DEL BACKEND
        const mensajeError = e.response?.data?.detail || 'No se pudo guardar los cambios';
        
        Swal.fire('Error', mensajeError, 'error');
    }
};

const eliminarGrupo = async (id, nombre) => {
    const res = await Swal.fire({
        title: `¿Borrar Grupo ${nombre}?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, borrar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#d33'
    });
    if (res.isConfirmed) {
        try {
            await grupoService.eliminar(id);
            await initData();
        } catch (error) {
            Swal.fire('Error', 'No se pudo eliminar', 'error');
        }
    }
};

const volver = () => router.back();







</script>

<template>
    <div class="page-content">
        <div class="view-header">
            <div class="header-left">
                <button @click="volver" class="btn-icon-back" title="Volver">
                    <i class="fas fa-arrow-left"></i> ←
                </button>
                <div>
                    <h1 class="title">Gestión de Grupos</h1>
                    <p class="subtitle">Asigna aulas y docentes a los cursos aperturados</p>
                </div>
            </div>
            <div class="header-right">
                <div class="stats-box">
                    <strong>{{ cursosList.length }}</strong> Cursos Totales
                </div>
            </div>
        </div>

        <div v-if="loading" class="loading-state">
            <div class="spinner"></div> Cargando datos...
        </div>

        <div v-else class="courses-container">
            
            <div v-for="grupoCiclo in cursosPorCiclo" :key="grupoCiclo.titulo" class="cycle-block">
                
                <div class="cycle-separator">
                    <span class="cycle-title">Ciclo {{ grupoCiclo.titulo }}</span>
                    <div class="line"></div>
                </div>

                <div class="courses-list">
                    <div v-for="cursoAp in grupoCiclo.cursos" :key="cursoAp.id" class="course-row">
                        
                        <div class="col-info">
                            <span class="course-code">{{ cursoAp.curso.codigo }}</span>
                            <h3 class="course-name">{{ cursoAp.curso.nombre }}</h3>
                        </div>

                        <div class="col-groups">
                            <div v-if="cursoAp.grupos && cursoAp.grupos.length > 0" class="tags-container">
                               <div v-for="grupo in cursoAp.grupos" :key="grupo.id" class="group-tag" 
                                    :title="grupo.docente ? grupo.docente.nombre_completo : 'Sin docente asignado'">
                                    <div class="tag-info">
                                        <strong>G{{ grupo.nombre }}</strong>
                                        <small v-if="grupo.turno">{{ grupo.turno.nombre }}</small>
                                        <small class="docente-tag" :class="{'text-danger': !grupo.docente}">
                                            <i class="fas fa-user"></i> 
                                            {{ grupo.docente ? grupo.docente.apellido : 'Sin Docente' }}
                                        </small>
                                    </div>
                                    <button @click="editarGrupo(grupo, cursoAp)" class="btn-tag-edit">
                                        <i class="fas fa-pencil-alt"></i>
                                    </button>
                                    <button @click="eliminarGrupo(grupo.id, grupo.nombre)" class="btn-tag-remove">&times;</button>
                                </div>
                            </div>
                            <div v-else class="empty-state-text">
                                Sin grupos
                            </div>
                        </div>

                        <div class="col-actions">
                            <button @click="abrirModal(cursoAp)" class="btn-add-group">
                                + Grupo
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="cursosList.length === 0" class="no-data">
                No hay cursos aperturados para este periodo.
            </div>

        </div>

        <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
            <div class="modal-panel">
                <div class="modal-header">
                    <h3>Nuevo Grupo</h3>
                    <button class="close-btn" @click="showModal = false">&times;</button>
                </div>
                
                <div class="modal-body">
                    <div class="selected-course-info">
                        Curso: <strong>{{ cursoSeleccionado?.curso?.nombre }}</strong>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label>Turno</label>
                            <select v-model="form.id_turno" class="input-control">
                                <option v-for="t in turnos" :key="t.id" :value="t.id">{{ t.nombre }}</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Cantidad</label>
                            <input v-model.number="form.cantidad_grupos" type="number" min="1" max="4" class="input-control">
                        </div>
                    
                        <div class="form-group full-width">
                            <label>Docente (Opcional)</label>
                            <select class="input-control" v-model="form.id_docente">
                                <option value="" disabled>Seleccione un docente</option>
                                
                                <option v-for="docente in listaDocentes" :key="docente.id" :value="docente.id_docente">
                                    {{ docente.nombre }} {{ docente.apellido }}
                                </option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Vacantes</label>
                            <input v-model.number="form.vacantes_por_grupo" type="number" class="input-control">
                        </div>
                    </div>
                </div>

                <div class="modal-footer">
                    <button @click="showModal = false" class="btn-cancel">Cancelar</button>
                    <button @click="guardarGrupos" class="btn-confirm">Guardar</button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* --- Layout Base --- */
.page-content { padding: 1.5rem; font-family: 'Segoe UI', sans-serif; background-color: #f1f5f9; min-height: 100vh; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.title { font-size: 1.5rem; color: #1e293b; margin: 0; font-weight: 700; }
.subtitle { color: #64748b; font-size: 0.9rem; margin: 0; }
.btn-icon-back { border: none; background: transparent; font-size: 1.2rem; color: #64748b; cursor: pointer; }
.stats-box { background: #fff; padding: 5px 15px; border-radius: 20px; color: #475569; font-size: 0.9rem; border: 1px solid #e2e8f0;}

/* --- Separadores por Ciclo --- */
.cycle-block { margin-bottom: 2rem; }
.cycle-separator { display: flex; align-items: center; margin-bottom: 1rem; gap: 10px; }
.cycle-title { font-weight: 800; color: #3b82f6; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 0.5px; white-space: nowrap; }
.line { width: 100%; height: 1px; background: #cbd5e1; }

/* --- Lista Compacta --- */
.courses-list { display: flex; flex-direction: column; gap: 0.8rem; }
.course-row { display: flex; align-items: center; background: white; border-radius: 8px; padding: 0.8rem 1.2rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; transition: transform 0.1s; }
.course-row:hover { border-color: #cbd5e1; transform: translateX(2px); }

.col-info { flex: 0 0 250px; border-right: 1px solid #f1f5f9; padding-right: 1rem; margin-right: 1rem; }
.course-name { font-size: 1rem; margin: 0; color: #334155; font-weight: 600; }
.course-code { font-size: 0.75rem; color: #94a3b8; font-weight: bold; display: block; margin-bottom: 2px;}

.col-groups { flex: 1; display: flex; align-items: center; }
.tags-container { display: flex; flex-wrap: wrap; gap: 8px; }
.group-tag { display: flex; align-items: center; background: #f0fdf4; border: 1px solid #bbf7d0; padding: 4px 8px; border-radius: 6px; gap: 8px; }
.tag-info { display: flex; flex-direction: column; line-height: 1; }
.tag-info strong { color: #15803d; font-size: 0.85rem; }
.tag-info small { color: #86efac; font-size: 0.7rem; color: #166534; }
.btn-tag-remove { background: none; border: none; color: #ef4444; cursor: pointer; font-size: 1.1rem; padding: 0; line-height: 0.5; opacity: 0.6; }
.btn-tag-remove:hover { opacity: 1; }
.empty-state-text { color: #cbd5e1; font-style: italic; font-size: 0.9rem; }

.col-actions { margin-left: auto; padding-left: 1rem; }
.btn-add-group { background-color: #3b82f6; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.85rem; white-space: nowrap; transition: background 0.2s; }
.btn-add-group:hover { background-color: #2563eb; }

/* --- Modal Styles --- */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 100; }
.modal-panel { background: white; width: 90%; max-width: 450px; border-radius: 10px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
.modal-header { padding: 1rem 1.5rem; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
.modal-header h3 { margin: 0; font-size: 1.1rem; color: #334155; }
.close-btn { border: none; background: none; font-size: 1.5rem; cursor: pointer; color: #94a3b8; }
.modal-body { padding: 1.5rem; }
.selected-course-info { margin-bottom: 1.5rem; padding: 0.8rem; background: #eff6ff; color: #1e40af; border-radius: 6px; font-size: 0.9rem; text-align: center; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.full-width { grid-column: span 2; }
.form-group label { display: block; font-size: 0.8rem; font-weight: 600; color: #64748b; margin-bottom: 0.4rem; }
.input-control { width: 100%; padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.9rem; }
.modal-footer { padding: 1rem 1.5rem; background: #f8fafc; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; gap: 0.5rem; }
.btn-cancel { background: white; border: 1px solid #cbd5e1; color: #64748b; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; }
.btn-confirm { background: #10b981; border: none; color: white; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-weight: 600; }
.loading-state { text-align: center; padding: 3rem; color: #94a3b8; }
.spinner { display: inline-block; width: 20px; height: 20px; border: 2px solid #cbd5e1; border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s infinite linear; vertical-align: middle; margin-right: 8px;}
@keyframes spin { 100% { transform: rotate(360deg); } }
</style>