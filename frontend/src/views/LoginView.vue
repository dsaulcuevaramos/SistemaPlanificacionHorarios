<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore';

const router = useRouter();

const authStore = useAuthStore();
const username = ref('');
const password = ref('');
const loginFailed = ref(false); // Para la animación de error (shake)
const showSuccessOverlay = ref(false); // CRÍTICO: Para el overlay de pantalla completa

const goToRecovery = () => {
    // Asegúrate de que esta ruta coincida exactamente con la registrada en router/index.js
    router.push('/recuperacion-password');
} 

const handleLogin = async () => {
  // Validación de campos
  if (!username.value || !password.value) {
    authStore.error = "Por favor complete todos los campos";
    loginFailed.value = true;
    setTimeout(() => { loginFailed.value = false; }, 600);
    return;
  }

  // Reseteamos estados
  loginFailed.value = false;
  authStore.error = null;

  try {
    const success = await authStore.login(username.value, password.value);
    
    if (success) {
      // 1. ÉXITO: Mostrar la animación de pantalla completa
      showSuccessOverlay.value = true;
      
      // 2. Esperar 1.8 segundos para que la animación se vea bien antes de redirigir
      setTimeout(() => {
        router.push('/dashboard');
      }, 1000); 
    }

  } catch (e) {
    // 3. FALLO: El error ya está capturado en authStore.error
    password.value = ''; // Limpiamos la contraseña
    loginFailed.value = true;
    setTimeout(() => { loginFailed.value = false; }, 600);
  }
};
</script>

<template>
  <div class="login-page">
    
    <div class="background-overlay"></div>

    <transition name="fade">
      <div v-if="showSuccessOverlay" class="success-overlay">
         <div class="success-content">
          <div class="success-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2>¡BIENVENIDO!</h2>
          <p>Credenciales verificadas correctamente.</p>
          <p class="redirect-text">Ingresando al sistema...</p>
        </div>
      </div>
    </transition>


    <div class="login-wrapper">
      
      <div v-if="!showSuccessOverlay" class="login-card" :class="{ 'shake': loginFailed }">
        
        <div class="form-content">
          <div class="brand-header">
            <div class="logo-icon">🎓</div>
            <h1>SISTEMA DE HORARIOS</h1>
            <p class="subtitle">UNIVERSIDAD NACIONAL DE UCAYALI</p>
          </div>

          <form @submit.prevent="handleLogin">
            
            <div class="input-group">
              <span class="input-icon">👤</span>
              <input 
                type="text" 
                v-model="username" 
                placeholder="Usuario o email *" 
                :disabled="authStore.loading"
                required
              />
            </div>

            <div class="input-group">
              <span class="input-icon">🔒</span>
              <input 
                type="password" 
                v-model="password" 
                placeholder="Contraseña *" 
                :disabled="authStore.loading"
                required
              />
            </div>

            <div v-if="authStore.error" class="error-message">
              ⚠️ {{ authStore.error }}
            </div>

            <button type="submit" class="btn-login" :class="{ 'loading': authStore.loading }" :disabled="authStore.loading">
              <span v-if="!authStore.loading">INGRESAR AL SISTEMA</span>
              <span v-else class="loader"></span>
            </button>

          </form>
          <br>
          <div class="footer-links">
              <a href="#" @click.prevent="router.push('/recuperar-password')" class="forgot-link">
                  ¿Olvidaste tu contraseña?
              </a>
              <p>Universidad nacional de Ucayali</p>
          </div>
     
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* --- 1. FONDO Y LAYOUT --- */
.login-page { height: 100vh; width: 100%; display: flex; justify-content: center; align-items: center; position: relative; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; overflow: hidden; }
.background-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: url('https://images.unsplash.com/photo-1497294815431-9365093b7331?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80') no-repeat center center/cover; box-shadow: inset 0 0 0 1000px rgba(15, 23, 42, 0.85); z-index: 1; filter: blur(2px); }
.login-wrapper { position: relative; z-index: 10; width: 100%; max-width: 500px; padding: 20px; }

/* --- 2. TARJETA --- */
.login-card { background: rgba(255, 255, 255, 1); border-radius: 16px; padding: 40px 30px; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3); text-align: center; transition: transform 0.3s ease; min-height: 500px; display: flex; flex-direction: column; justify-content: center; }
.brand-header { margin-bottom: 30px; }
.logo-icon { font-size: 3rem; margin-bottom: 10px; display: inline-block; background: #f0f9ff; border-radius: 50%; width: 80px; height: 80px; line-height: 80px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
.brand-header h1 { font-size: 1.4rem; color: #1e293b; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
.subtitle { color: #64748b; font-size: 0.75rem; font-weight: 600; margin-top: 5px; letter-spacing: 1px; }

.input-group { position: relative; margin-bottom: 20px; }
.input-icon { position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 1.1rem; }
.input-group input { width: 85%; padding: 14px 15px 14px 45px; border: 2px solid #f1f5f9; background-color: #f8fafc; border-radius: 8px; font-size: 0.95rem; color: #334155; transition: all 0.3s; outline: none; }
.input-group input:focus { border-color: #3b82f6; background-color: #fff; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1); }

.btn-login { width: 100%; padding: 14px; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 700; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; margin-top: 10px; display: flex; justify-content: center; align-items: center; }
.btn-login:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(37, 99, 235, 0.2); }
.btn-login:disabled { background: #cbd5e1; cursor: not-allowed; }

.footer-links p { margin-top: 30px; font-size: 0.75rem; color: #94a3b8; }

.error-message { color: #ef4444; background-color: #fef2f2; padding: 10px; border-radius: 6px; font-size: 0.85rem; margin-bottom: 20px; border: 1px solid #fecaca; animation: fadeIn 0.3s; }

/* --- 3. ANIMACIONES Y CRÍTICO DE ÉXITO --- */

/* OVERLAY DE PANTALLA COMPLETA (CRÍTICO: SOLUCIONA EL FREEZE EN EL RECUADRO) */
.success-overlay {
  position: fixed; /* Esto asegura que cubre toda la ventana */
  top: 0; left: 0; width: 100vw; height: 100vh;
  /* Fondo semi-transparente que permite ver el fondo borroso */
  background: rgba(255, 255, 255, 0.95); 
  z-index: 100; /* Alto z-index para estar por encima de todo */
  display: flex; justify-content: center; align-items: center;
}

/* Contenido de éxito (Estilos originales del usuario) */
.success-content { animation: fadeIn 0.5s ease-out; color: #334155; text-align: center; }
.success-icon { width: 80px; height: 80px; background-color: #dcfce7; color: #16a34a; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto; box-shadow: 0 0 0 10px rgba(220, 252, 231, 0.5); }
.success-icon svg { width: 40px; height: 40px; animation: checkPop 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
@keyframes checkPop { 0% { transform: scale(0); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
.success-content h2 { color: #16a34a; margin-bottom: 10px; }
.redirect-text { font-size: 0.85rem; color: #64748b; margin-top: 20px; font-style: italic; }

/* Animaciones */
.loader { width: 20px; height: 20px; border: 3px solid #fff; border-bottom-color: transparent; border-radius: 50%; display: inline-block; animation: rotation 1s linear infinite; }
@keyframes rotation { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.shake { animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both; }
@keyframes shake { 10%, 90% { transform: translate3d(-1px, 0, 0); } 20%, 80% { transform: translate3d(2px, 0, 0); } 30%, 50%, 70% { transform: translate3d(-4px, 0, 0); } 40%, 60% { transform: translate3d(4px, 0, 0); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
</style>