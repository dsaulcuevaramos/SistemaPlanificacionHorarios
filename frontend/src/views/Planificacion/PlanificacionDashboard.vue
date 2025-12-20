<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();
const navigateTo = (path) => router.push(path);
</script>

<template>
  <div class="page-content dashboard-planificacion">
    
    <div class="view-header">
      <div>
        <h1 class="title">Módulo de Planificación</h1>
        <p class="subtitle">Gestión de recursos y entidades académicas base.</p>
      </div>
    </div>

    <div class="cards-grid">
      
      <div class="dashboard-card card-docentes" @click="navigateTo('/docentes')">
        <div class="card-icon-bg">🧑‍🏫</div>
        <div class="card-body">
          <h3>REGISTRO DE DOCENTES</h3>
          <p class="description">Administración de la plana docente, DNI, emails y carga horaria máxima.</p>
          <ul class="features-list">
            <li>• CRUD de Docentes</li>
            <li>• Asignación de Contratos</li>
          </ul>
        </div>
        <div class="card-footer">
          <span>Ir a Docentes</span>
          <span class="arrow">→</span>
        </div>
      </div>

      <div class="dashboard-card card-cursos" @click="navigateTo('/cursos')">
        <div class="card-icon-bg">📚</div>
        <div class="card-body">
          <h3>REGISTRO DE CURSOS</h3>
          <p class="description">Gestión de asignaturas, créditos, horas teóricas y prácticas por plan.</p>
          <ul class="features-list">
            <li>• CRUD de Asignaturas</li>
            <li>• Tipos (Obligatorio/Electivo)</li>
          </ul>
        </div>
        <div class="card-footer">
          <span>Ir a Cursos</span>
          <span class="arrow">→</span>
        </div>
      </div>

      <div class="dashboard-card card-aulas" @click="navigateTo('/aulas')">
        <div class="card-icon-bg">🏢</div>
        <div class="card-body">
          <h3>AULAS</h3>
          <p class="description">Gestión de espacios físicos, pabellones, aforo y recursos tecnológicos necesarios.</p>
          <ul class="features-list">
            <li>• CRUD de Aulas</li>
            <li>• Aforo y Recursos (JSON)</li>
          </ul>
        </div>
        <div class="card-footer">
          <span>Ir a Aulas</span>
          <span class="arrow">→</span>
        </div>
      </div>
      
      <div class="dashboard-card card-planes" @click="navigateTo('/planEstudio')">
        <div class="card-icon-bg">🎓</div>
        <div class="card-body">
          <h3>PLANES DE ESTUDIO</h3>
          <p class="description">Configuración de mallas curriculares, versiones y ciclos académicos.</p>
          <ul class="features-list">
            <li>• Versiones de Planes</li>
            <li>• Mapeo a Cursos</li>
          </ul>
        </div>
        <div class="card-footer">
          <span>Ir a Planes</span>
          <span class="arrow">→</span>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* REUTILIZACIÓN DE ESTILOS DEL DASHBOARD HOME Y DOCENTES VIEW */
.page-content { padding: 2rem; max-width: 1400px; margin: 0 auto; }
.view-header { display: flex; justify-content: space-between; align-items: end; margin-bottom: 2rem; }
.title { font-size: 1.8rem; color: #1e293b; font-weight: 700; margin: 0; }
.subtitle { color: #64748b; font-size: 0.95rem; margin: 0; }

.cards-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
  gap: 2rem;
}

.dashboard-card {
  background: white; border-radius: 16px; overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease; cursor: pointer; border: 1px solid #f1f5f9;
  position: relative; display: flex; flex-direction: column;
}
.dashboard-card:hover { transform: translateY(-8px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }

/* Colores Específicos */
.card-docentes { border-top: 5px solid #06b6d4; } /* Cian */
.card-cursos { border-top: 5px solid #f59e0b; } /* Amarillo/Naranja */
.card-aulas { border-top: 5px solid #8b5cf6; } /* Morado */
.card-planes { border-top: 5px solid #10b981; } /* Verde */

.card-icon-bg { position: absolute; top: 1rem; right: 1rem; font-size: 4rem; opacity: 0.05; transition: 0.3s; }
.dashboard-card:hover .card-icon-bg { transform: scale(1.2) rotate(10deg); opacity: 0.1; }

.card-body { padding: 2rem; flex: 1; }
.card-body h3 { font-size: 1.2rem; color: #1e293b; margin-bottom: 0.5rem; font-weight: 800; }
.description { color: #64748b; font-size: 0.9rem; min-height: 40px; }

.features-list { list-style: none; padding: 0; color: #475569; font-size: 0.85rem; margin-top: 15px; }
.features-list li { margin-bottom: 5px; padding-left: 5px; }

.card-footer {
  padding: 1rem 2rem; background-color: #f8fafc; border-top: 1px solid #e2e8f0;
  display: flex; justify-content: space-between; align-items: center;
  color: #64748b; font-weight: 600; font-size: 0.9rem; transition: 0.2s;
}
.dashboard-card:hover .card-footer { background-color: #f0f9ff; color: #3b82f6; }
.arrow { transition: transform 0.2s; }
.dashboard-card:hover .arrow { transform: translateX(5px); }
</style>