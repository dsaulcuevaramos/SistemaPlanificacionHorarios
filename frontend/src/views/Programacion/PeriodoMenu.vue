<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

// Obtenemos el ID del periodo de la URL (ej: /programacion/periodo/1)
const idPeriodo = route.params.id;

// Simulación: En el futuro, harás un fetch aquí para obtener el nombre del periodo (ej. "2025-I")
// const { data: periodo } = useFetch(`/api/periodos/${idPeriodo}`)
const nombrePeriodo = computed(() => `Periodo Académico (ID: ${idPeriodo})`);

const navegarA = (modulo) => {
  // Navegamos a las rutas hijas manteniendo el contexto del periodo
  router.push(`/programacion/periodo/${idPeriodo}/${modulo}`);
};

const volver = () => {
  router.push('/programacion');
};
</script>

<template>
  <div class="page-content periodo-menu">
    
    <div class="view-header">
      <div class="flex items-center gap-4">
        <button @click="volver" class="btn-back">
          ← Volver
        </button>
        <div>
          <h1 class="title">{{ nombrePeriodo }}</h1>
          <p class="subtitle">Seleccione el área de gestión para este ciclo.</p>
        </div>
      </div>
    </div>

    <div class="cards-grid">
      
      <div class="dashboard-card card-cursos" @click="navegarA('cursos')">
        <div class="card-icon-bg">📚</div>
        <div class="card-body">
          <div class="icon-wrapper bg-blue-100 text-blue-600">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
            </svg>
          </div>
          <h3>PROGRAMACIÓN DE CURSOS</h3>
          <p class="description">
            Visualizar, asignar horarios y gestionar la carga académica de los cursos para este periodo.
          </p>
        </div>
        <div class="card-footer">
          <span>Ver Programación</span>
          <span class="arrow">→</span>
        </div>
      </div>

      <div class="dashboard-card card-docentes" @click="navegarA('docentes')">
        <div class="card-icon-bg">👔</div>
        <div class="card-body">
          <div class="icon-wrapper bg-indigo-100 text-indigo-600">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
            </svg>
          </div>
          <h3>CONTRATOS DOCENTES</h3>
          <p class="description">
            Administrar la plana docente, asignar contratos y verificar disponibilidad para este periodo.
          </p>
        </div>
        <div class="card-footer">
          <span>Ver Docentes</span>
          <span class="arrow">→</span>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* Estilos Base */
.page-content { padding: 2rem; max-width: 1000px; margin: 0 auto; } /* Ancho más contenido para 2 opciones */
.view-header { margin-bottom: 3rem; }
.title { font-size: 1.8rem; color: #1e293b; font-weight: 700; margin: 0; }
.subtitle { color: #64748b; font-size: 1rem; margin: 0; }

/* Botón Volver */
.btn-back {
  background: transparent; border: 1px solid #e2e8f0; color: #64748b;
  padding: 0.5rem 1rem; cursor: pointer; transition: 0.2s;
  font-weight: 600; font-size: 0.9rem;
}
.btn-back:hover { background: #f1f5f9; color: #334155; border-color: #cbd5e1; }

/* Grid de 2 Columnas */
.cards-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
  gap: 2rem;
}

/* Tarjetas */
.dashboard-card {
  background: white; border-radius: 16px; overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease; cursor: pointer; border: 1px solid #f1f5f9;
  position: relative; display: flex; flex-direction: column;
  height: 100%;
}
.dashboard-card:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }

/* Colores Superiores */
.card-cursos { border-top: 6px solid #3b82f6; }   /* Azul */
.card-docentes { border-top: 6px solid #6366f1; } /* Indigo */

/* Icono de Fondo decorativo */
.card-icon-bg { position: absolute; top: 1rem; right: 1rem; font-size: 5rem; opacity: 0.05; transition: 0.3s; pointer-events: none; }
.dashboard-card:hover .card-icon-bg { transform: scale(1.1) rotate(5deg); opacity: 0.1; }

.card-body { padding: 2.5rem 2rem; flex: 1; display: flex; flex-direction: column; align-items: center; text-align: center; }

/* Icono Central */
.icon-wrapper {
  padding: 1rem; border-radius: 50%; margin-bottom: 1.5rem;
}

.card-body h3 { font-size: 1.25rem; color: #1e293b; margin-bottom: 1rem; font-weight: 800; }
.description { color: #64748b; font-size: 0.95rem; line-height: 1.6; }

/* Footer de Tarjeta */
.card-footer {
  padding: 1.2rem 2rem; background-color: #f8fafc; border-top: 1px solid #e2e8f0;
  display: flex; justify-content: space-between; align-items: center;
  color: #64748b; font-weight: 600; font-size: 0.9rem; transition: 0.2s;
}
.dashboard-card:hover .card-footer { background-color: #f0f9ff; color: #3b82f6; }
.arrow { transition: transform 0.2s; }
.dashboard-card:hover .arrow { transform: translateX(5px); }
</style>