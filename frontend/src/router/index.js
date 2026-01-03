import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/authStore';

// Layouts
import MainLayout from '../layouts/MainLayout.vue';

// --- VISTAS GENERALES ---
import LoginView from '../views/LoginView.vue';
import RecuperarView from '../views/RecoveryView.vue';
import DashboardHome from '../views/DashboardHomeView.vue'; 

// --- VISTAS PROGRAMACIÓN ---
import PeriodoMenu from '../views/Programacion/PeriodoMenu.vue';
import CursosPeriodo from '../views/Programacion/CursosPeriodo.vue';
import DocentesPeriodo from '../views/Programacion/DocentesPeriodo.vue';
import GrupoPeriodo from '../views/Programacion/GrupoPeriodo.vue';

// --- VISTAS GESTIÓN DE HORARIOS (Corregidas) ---
// Asegúrate de que los archivos existan en estas rutas exactas
import GestionDashboardView from '../views/Gestion/GestionDashboardView.vue';
import GenerarBloquesView from '../views/Gestion/BloquesView.vue'; // O GenerarBloquesView.vue según como guardaste el archivo
import GestionHorarioMainView from '../views/Gestion/GestionHorarioMainView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // 1. Login y Recuperación (Públicas)
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresAuth: false }
    },
    {
      path: '/recuperar-password',
      name: 'recovery',
      component: RecuperarView,  
    },

    // 2. Layout Principal (Protegido)
    {
      path: '/',
      name: 'MainLayout',
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '/dashboard',
          name: 'dashboard',
          component: DashboardHome
        },

        // ==========================================
        // MÓDULO PLANIFICACIÓN
        // ==========================================
        {
          path: '/planificacion',
          name: 'planificacion_dashboard',
          component: () => import('../views/Planificacion/PlanificacionDashboard.vue'),
        },
        {
          path: '/docentes',
          name: 'docentes',
          component: () => import('../views/Planificacion/DocentesView.vue'),
        },
        {
          path: '/cursos',
          name: 'cursos',
          component: () => import('../views/Planificacion/CursosView.vue'),
        },
        {
          path: '/aulas',
          name: 'aulas',
          component: () => import('../views/Planificacion/AulasView.vue'),
        },
        {
          path: '/planEstudio',
          name: 'planEstudio',
          component: () => import('../views/Planificacion/PlanEstudioView.vue'),
        },
        {
          path: '/turnos',
          name: 'turnos',
          component: () => import('../views/TurnosView.vue'),
        },

        // ==========================================
        // MÓDULO PROGRAMACIÓN ACADÉMICA
        // ==========================================
        {
          path: '/programacion',
          name: 'programacion',
          component: () => import('../views/Programacion/ProgramacionView.vue'),
        },
        {
          path: '/programacion/periodo/:id',
          name: 'PeriodoMenu',
          component: PeriodoMenu,
        },
        {
          path: '/programacion/periodo/:id/cursos',
          name: 'CursosPeriodo',
          component: CursosPeriodo
        },
        {
          path: '/programacion/periodo/:id/docentes',
          name: 'DocentesPeriodo',
          component: DocentesPeriodo
        },
        {
          path: '/programacion/periodo/:id/grupos',
          name: 'GruposPeriodo',
          component: GrupoPeriodo
        },

        // ==========================================
        // MÓDULO GESTIÓN DE HORARIOS (NUEVO)
        // ==========================================
        {
          path: '/gestion-horarios',
          name: 'gestion-dashboard',
          component: GestionDashboardView,
          meta: { title: 'Gestión de Horarios' }
        },
        {
          path: '/gestion-horarios/configurar-bloques',
          name: 'configurar-bloques',
          component: GenerarBloquesView,
          meta: { title: 'Configurar Bloques' }
        },
        {
          // Esta ruta recibe el ID del periodo para cargar grupos y horarios
          path: '/gestion-horarios/periodo/:id_periodo/asignacion',
          name: 'asignacion-horarios',
          component: GestionHorarioMainView,
          props: true, // ¡IMPORTANTE! Esto pasa el parametro :id_periodo como prop al componente
          meta: { title: 'Asignación de Horarios' }
        }
      ]
    }
  ]
});


router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();
    const publicRoutes = ['login', 'recovery']; // ¡AÑADIR 'recovery' aquí! 
    const requiresAuth = !publicRoutes.includes(to.name); // 2. Comprobar si la ruta requiere autenticación

    if (!authStore.isAuthenticated && requiresAuth) {
        if (to.name === 'dashboard' || to.name === 'MainLayout') {
            next({ name: 'login' });
        } else {
            next({ name: 'login' });
        }
    }  
    else if (authStore.isAuthenticated && to.name === 'login') {
        next({ name: 'dashboard' });
    }
    else {
        next();
    }
});


export default router;