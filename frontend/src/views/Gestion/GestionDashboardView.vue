<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
// Importa tu servicio real de periodos
import periodoService from '../../api/periodoService'; 

const router = useRouter();
const periodos = ref([]);
const idPeriodoSeleccionado = ref(null); // Aquí guardamos lo que el usuario elija
const loading = ref(true);

onMounted(async () => {
    try {
        // Traemos TODOS los periodos (o solo los activos, según tu lógica de negocio)
        const response = await periodoService.getAll();
        periodos.value = response; 
        
        // Opcional: Si hay periodos, pre-seleccionar el primero o el marcado como 'actual'
        if (periodos.value.length > 0) {
            // Lógica: busca el activo, si no hay, agarra el último creado (o el primero de la lista)
            const activo = periodos.value.find(p => p.estado === 1) || periodos.value[0];
            idPeriodoSeleccionado.value = activo.id;
        }
    } catch (e) {
        console.error("Error cargando periodos", e);
    } finally {
        loading.value = false;
    }
});

const irAAsignacion = () => {
    if (idPeriodoSeleccionado.value) {
        // Redirigimos pasando el ID que el usuario escogió explícitamente
        router.push({ 
            name: 'asignacion-horarios', 
            params: { id_periodo: idPeriodoSeleccionado.value } 
        });
    }
};
</script>

<template>
    <div class="dashboard-container">
        <header class="dash-header">
            <h1>Módulo de Gestión de Horarios</h1>
            <p class="subtitle">Administración de tiempos y carga académica</p>
        </header>
        
        <div v-if="loading" class="loading-state">
            <div class="spinner"></div> Cargando periodos...
        </div>
        
        <div v-else class="cards-grid">
            <div class="card" @click="router.push({ name: 'configurar-bloques' })">
                <div class="card-icon blue-icon">⚙️</div>
                <div class="card-content">
                    <h2>1. Configuración de Bloques</h2>
                    <p>Define la estructura temporal (horas y turnos) base para la institución.</p>
                    <span class="link-text">Ir a configuración &rarr;</span>
                </div>
            </div>

            <div class="card operation-card">
                <div class="card-icon indigo-icon">📅</div>
                
                <div class="card-content">
                    <h2>2. Asignación de Horarios</h2>
                    <p>Selecciona un periodo académico para comenzar a programar las clases.</p>
                    
                    <div class="selector-area">
                        <label for="periodo-select">Seleccionar Periodo:</label>
                        <select id="periodo-select" v-model="idPeriodoSeleccionado" class="periodo-select">
                            <option v-for="p in periodos" :key="p.id" :value="p.id">
                                {{ p.nombre || p.codigo }}  </option>
                        </select>
                    </div>

                    <button 
                        @click="irAAsignacion" 
                        class="btn-action" 
                        :disabled="!idPeriodoSeleccionado"
                    >
                        Gestionar Asignaciones &rarr;
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Estilos Base (Reutilizando los anteriores y agregando los nuevos) */
.dashboard-container {
    padding: 3rem;
    background-color: #f8f9fa;
    min-height: 100vh;
    font-family: 'Segoe UI', sans-serif;
}

.dash-header { margin-bottom: 3rem; }
.dash-header h1 { font-size: 1.8rem; color: #1e293b; margin-bottom: 0.5rem; }
.subtitle { color: #64748b; }

.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
    max-width: 1000px;
}

.card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

/* Efecto hover solo en la tarjeta 1 que es clickeable entera */
.card:not(.operation-card):hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.05);
    cursor: pointer;
}

.operation-card {
    border-color: #6366f1; /* Borde resaltado para la acción principal */
    background: #fff;
}

.card-icon {
    width: 50px; height: 50px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 12px; font-size: 1.5rem;
}
.blue-icon { background-color: #eff6ff; color: #3b82f6; }
.indigo-icon { background-color: #eef2ff; color: #6366f1; }

.card-content h2 { font-size: 1.25rem; color: #334155; margin-bottom: 0.5rem; }
.card-content p { color: #64748b; font-size: 0.95rem; line-height: 1.5; margin-bottom: 1.5rem; }

.link-text { color: #3b82f6; font-weight: 600; font-size: 0.9rem; }

/* NUEVOS ESTILOS PARA EL SELECTOR Y BOTÓN */
.selector-area {
    margin-bottom: 1.5rem;
    background: #f8fafc;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
}

.selector-area label {
    display: block;
    font-size: 0.8rem;
    font-weight: 700;
    color: #475569;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
}

.periodo-select {
    width: 100%;
    padding: 0.6rem;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 1rem;
    color: #1e293b;
    background-color: white;
    outline: none;
    transition: border 0.2s;
}

.periodo-select:focus {
    border-color: #6366f1;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.btn-action {
    width: 100%;
    padding: 0.8rem;
    background-color: #4f46e5;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
}

.btn-action:hover:not(:disabled) {
    background-color: #4338ca;
}

.btn-action:disabled {
    background-color: #cbd5e1;
    cursor: not-allowed;
    opacity: 0.8;
}

.loading-state { text-align: center; color: #64748b; padding: 2rem; }
.spinner { /* Estilos de spinner simple si gustas */ display: inline-block; width: 20px; height: 20px; border: 3px solid rgba(0,0,0,0.1); border-radius: 50%; border-top-color: #4f46e5; animation: spin 1s ease-in-out infinite; margin-right: 10px; vertical-align: middle; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
