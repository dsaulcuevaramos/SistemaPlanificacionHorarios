<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore';

const router = useRouter();
const authStore = useAuthStore();
const userName = authStore.user?.username || 'Admin';

const isSidebarOpen = ref(true);
const openMenus = ref({
  planificacion: true,
  programacion: false, // Ya estaba declarado, ahora lo usaremos
  gestion: false
});

const toggleSidebar = () => isSidebarOpen.value = !isSidebarOpen.value;
const toggleMenu = (menu) => { openMenus.value[menu] = !openMenus.value[menu]; };
const navigateTo = (path) => { router.push(path); };
const handleLogout = () => { authStore.logout(); };
</script>

<template>
  <div class="app-layout">
    
    <aside :class="['sidebar', { 'sidebar-collapsed': !isSidebarOpen }]">
      <div class="sidebar-header">
        <div class="logo-area" v-if="isSidebarOpen">
          <div class="logo-circle">UNU</div>
          <span>SISTEMA</span>
        </div>
        <button @click="toggleSidebar" class="toggle-btn">☰</button>
      </div>

      <div class="sidebar-menu">
        <div class="menu-item" @click="navigateTo('/dashboard')">
          <span class="icon">🏠</span> <span v-if="isSidebarOpen">Inicio</span>
        </div>

        <div class="divider" v-if="isSidebarOpen">MÓDULOS</div>

        <div class="menu-group">
          <div 
            class="menu-header" 
            @click="toggleMenu('planificacion')" 
            :class="{ 'active': openMenus.planificacion }"
          >
            <div class="left" @click.stop="navigateTo('/planificacion')"> 
                <span class="icon">📅</span> 
                <span class="text" v-if="isSidebarOpen">Planificación</span>
            </div>
            <span class="arrow" v-if="isSidebarOpen" @click.stop="toggleMenu('planificacion')">
              {{ openMenus.planificacion ? '−' : '+' }}
            </span>
          </div>
          
          <div class="submenu" v-if="openMenus.planificacion && isSidebarOpen">
            <a @click="navigateTo('/docentes')">Docentes</a>
            <a @click="navigateTo('/cursos')">Cursos</a>
            <a @click="navigateTo('/aulas')">Aulas</a>
            <a @click="navigateTo('/planEstudio')">Planes de Estudio</a>
            <a @click="navigateTo('/turnos')">Turnos</a>
          </div>
        </div>

        <div class="menu-group">
          <div 
            class="menu-header" 
            @click="toggleMenu('programacion')" 
            :class="{ 'active': openMenus.programacion }"
          >
            <div class="left" @click.stop="navigateTo('/programacion')"> 
                <span class="icon">📆</span> 
                <span class="text" v-if="isSidebarOpen">Programación</span>
            </div>
          </div>
        </div>


        <div class="menu-group">
          <div 
            class="menu-header" 
            @click="toggleMenu('Gestion Horarios')" 
            :class="{ 'active': openMenus.programacion }"
          >
            <div class="left" @click.stop="navigateTo('/gestion-horarios')"> 
                <span class="icon">📆</span> 
                <span class="text" v-if="isSidebarOpen">Gestion Horarios</span>
            </div>
          </div>
        </div>


      </div>

      <div class="sidebar-footer">
        <button @click="handleLogout" class="btn-logout">
          <span class="icon">🚪</span> <span v-if="isSidebarOpen">Cerrar Sesión</span>
        </button>
      </div>
    </aside>

    <div class="main-wrapper">
      <header class="topbar">
        <div class="breadcrumbs">UNU / <b>Panel</b></div>
        <div class="user-profile">
          <div class="avatar">{{ userName.charAt(0).toUpperCase() }}</div>
          <span class="name">{{ userName }}</span>
        </div>
      </header>

      <main class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>