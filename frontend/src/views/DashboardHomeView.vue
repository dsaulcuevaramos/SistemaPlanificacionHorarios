<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();
const navigateTo = (path) => router.push(path);
</script>

<template>
  <div class="dashboard-home">
    
    <div class="welcome-banner">
      <h2>Panel de Control General</h2>
      <p>Seleccione un módulo principal para comenzar a gestionar.</p>
    </div>

    <div class="cards-grid">
      
      <div class="dashboard-card card-planning" @click="navigateTo('/planificacion')">
        <div class="card-icon-bg">📅</div>
        <div class="card-body">
          <h3>PLANIFICACIÓN</h3>
          <p class="description">Organizar y administrar los recursos base de la escuela.</p>
          <div class="divider"></div>
          <ul class="features-list">
            <li>• Docentes y Contratos</li>
            <li>• Planes y Cursos</li>
            <li>• Aulas e Infraestructura</li>
            <li>• Catálogos Base</li>
          </ul>
        </div>
        <div class="card-footer">
          <span>Ir a Planificación</span>
          <span class="arrow">→</span>
        </div>
      </div>

      <div class="dashboard-card card-programming" @click="navigateTo('/programacion')">
        <div class="card-icon-bg">⚡</div>
        <div class="card-body">
          <h3>PROGRAMACIÓN</h3>
          <p class="description">Integración de entidades y apertura de ciclos.</p>
          <div class="divider"></div>
          <ul class="features-list">
            <li>• Apertura de Semestre</li>
            <li>• Creación de Grupos</li>
            <li>• Asignación de Docentes</li>
            <li>• Definición de Bloques</li>
          </ul>
        </div>
        <div class="card-footer">
          <span>Ir a Programación</span>
          <span class="arrow">→</span>
        </div>
      </div>
      
      <div class="dashboard-card card-management" @click="navigateTo('/gestion-horarios')">
        <div class="card-icon-bg">📊</div>
        <div class="card-body">
          <h3>GESTIÓN DE HORARIOS</h3>
          <p class="description">Visualización y control de sesiones académicas.</p>
          <div class="divider"></div>
          <ul class="features-list">
            <li>• Grid de Horarios</li>
            <li>• Validación de Cruces</li>
            <li>• Reportes de Carga</li>
            <li>• Autogeneración</li>
          </ul>
        </div>
        <div class="card-footer">
          <span>Ir a Gestión</span>
          <span class="arrow">→</span>
        </div>
      </div>

    </div>
  </div>
</template>


<style scoped>
.dashboard-home { padding: 2rem; max-width: 1400px; margin: 0 auto; }
.welcome-banner { margin-bottom: 2.5rem; }
.welcome-banner h2 { font-size: 1.8rem; color: #1e293b; margin-bottom: 0.5rem; font-weight: 800; }
.welcome-banner p { color: #64748b; }

.cards-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); 
  gap: 2rem; 
}

.dashboard-card {
  background: white; border-radius: 16px; overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease; cursor: pointer; border: 1px solid #f1f5f9;
  position: relative; display: flex; flex-direction: column;
}
.dashboard-card:hover { transform: translateY(-8px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }

/* Bordes Superiores */
.card-planning { border-top: 5px solid #8b5cf6; } /* Morado */
.card-management { border-top: 5px solid #3b82f6; } /* Azul */
.card-programming { border-top: 5px solid #10b981; } /* Verde */

.card-icon-bg {
  position: absolute; top: 1rem; right: 1rem; font-size: 4rem; opacity: 0.05; transition: 0.3s;
}
.dashboard-card:hover .card-icon-bg { transform: scale(1.2) rotate(10deg); opacity: 0.1; }

.card-body { padding: 2rem; flex: 1; }
.card-body h3 { font-size: 1.3rem; color: #1e293b; margin-bottom: 0.5rem; font-weight: 800; }
.description { color: #64748b; font-size: 0.95rem; min-height: 45px; }

.divider { height: 1px; background: #f1f5f9; margin: 1.5rem 0; }

.features-list { list-style: none; padding: 0; color: #475569; font-size: 0.9rem; }
.features-list li { margin-bottom: 8px; padding-left: 5px; }

.card-footer {
  padding: 1rem 2rem; background-color: #f8fafc; border-top: 1px solid #f1f5f9;
  display: flex; justify-content: space-between; align-items: center;
  color: #64748b; font-weight: 600; font-size: 0.9rem; transition: 0.2s;
}

.card-planning:hover .card-footer { color: #8b5cf6; background: #f5f3ff; }
.card-management:hover .card-footer { color: #3b82f6; background: #eff6ff; }
.card-programming:hover .card-footer { color: #10b981; background: #ecfdf5; }
.arrow { transition: transform 0.2s; }
.dashboard-card:hover .arrow { transform: translateX(5px); }
</style>