import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/authStore';

// Layouts
import MainLayout from '../layouts/MainLayout.vue';

// Vistas
import LoginView from '../views/LoginView.vue';
import RecuperarView from '../views/RecoveryView.vue';
import DashboardHome from '../views/DashboardHomeView.vue'; 
import PeriodoMenu from '../views/Programacion/PeriodoMenu.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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

        // --- MÓDULO PLANIFICACIÓN ---
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



        //// ---------------------------------------------------------------------------
        {
          path: '/programacion',
          name: 'programacion',
          component: () => import('../views/Programacion/ProgramacionView.vue'),
        },

        {
            // Esta ruta captura el ID del periodo (ej: /programacion/periodo/1)
            path: '/Programacion/periodo/:id',
            name: 'PeriodoMenu',
            component: PeriodoMenu,
            meta: { requiresAuth: true }
          },
          {
            // Ruta para la opción 1: Cursos
            path: '/programacion/periodo/:id/cursos',
            name: 'CursosPeriodo',
            component: () => import('../views/Programacion/CursosPeriodo.vue') // Lazy load
          },
          {
            // Ruta para la opción 2: Docentes
            path: '/programacion/periodo/:id/docentes',
            name: 'DocentesPeriodo',
            component: () => import('../views/Programacion/DocentesPeriodo.vue') // Lazy load
          },
          {
            path: '/programacion/periodo/:id/cursos',
            name: 'CursosPeriodo',
            // COINCIDIR MAYÚSCULAS/MINÚSCULAS AQUÍ:
            component: () => import('../views/Programacion/CursosPeriodo.vue') 
          },


          {
            path: '/programacion/periodo/:id/docentes',
            name: 'DocentesPeriodo',
            // COINCIDIR MAYÚSCULAS/MINÚSCULAS AQUÍ:
            component: () => import('../views/Programacion/DocentesPeriodo.vue')
          },



          {
            path: '/GestionBloques',
            name: 'GestionHorarios',
            // COINCIDIR MAYÚSCULAS/MINÚSCULAS AQUÍ:
            component: () => import('../views/Gestion/BloquesView.vue')
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