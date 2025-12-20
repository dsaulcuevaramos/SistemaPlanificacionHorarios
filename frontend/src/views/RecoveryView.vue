<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/authStore';

const router = useRouter();
const authStore = useAuthStore();

// --- ESTADOS DE LA VISTA ---
// 1: Validación inicial (Usuario/Email + DNI)
// 2: Mostrar éxito de validación y ofrecer opciones
// 3: Formulario de cambio de clave
const step = ref(1); 

// Datos de Validación
const usernameOrEmail = ref('');
const dni = ref('');

// Datos de Resultado y Cambio
const usernameFound = ref(''); // Para mostrar en el mensaje de éxito
const newPassword = ref('');
const confirmPassword = ref('');
const message = ref(''); // Mensajes de éxito/error locales
const isProcessing = ref(false);

// --- FUNCIONES DE NAVEGACIÓN ---
const goToLogin = () => router.push('/login');

// --- PASO 1: VALIDAR IDENTIDAD ---
const handleRecoveryValidation = async () => {
    if (!usernameOrEmail.value || !dni.value) {
        message.value = "Por favor, complete ambos campos.";
        return;
    }
    
    authStore.error = null;
    message.value = '';
    isProcessing.value = true;

    try {
        // La API solo valida el DNI y el usuario
        const data = await authStore.recoverPassword(usernameOrEmail.value, dni.value);
        
        usernameFound.value = data.username;

        // Pasar al paso 2: Mostrar éxito y opciones
        step.value = 2; 

    } catch (error) {
        // El error ya está en authStore.error (DNI incorrecto, Usuario no existe, etc.)
        message.value = authStore.error; 
    } finally {
        isProcessing.value = false;
    }
};

// --- PASO 2/3: CAMBIAR LA CLAVE ---
const handlePasswordReset = async () => {
    if (newPassword.value !== confirmPassword.value) {
        message.value = "Las contraseñas no coinciden.";
        return;
    }
    if (newPassword.value.length < 6) {
        message.value = "La contraseña debe tener al menos 6 caracteres.";
        return;
    }

    message.value = '';
    isProcessing.value = true;

    try {
        await authStore.resetPassword(usernameOrEmail.value, dni.value, newPassword.value);
        
        // Éxito: Volver al login con un mensaje temporal
        alert("Contraseña actualizada exitosamente. Ya puedes ingresar con tu nueva clave."); 
        goToLogin();

    } catch (error) {
        message.value = authStore.error; 
    } finally {
        isProcessing.value = false;
    }
};
</script>

<template>
    <div class="login-page">
        <div class="background-overlay"></div>
        <div class="login-wrapper">
            <div class="login-card">
                
                <div class="brand-header">
                    <h1>RECUPERAR CONTRASEÑA</h1>
                    <p class="subtitle">Validación de identidad por DNI</p>
                </div>
                
                <div v-if="authStore.error && !isProcessing" class="error-message">⚠️ {{ authStore.error }}</div>

                <form @submit.prevent="handleRecoveryValidation" v-if="step === 1">
                    <p class="instruction">Paso 1: Ingrese sus credenciales para validar su identidad.</p>
                    
                    <div class="input-group">
                        <span class="input-icon">👤</span>
                        <input type="text" v-model="usernameOrEmail" placeholder="Usuario o Email" required :disabled="isProcessing"/>
                    </div>

                    <div class="input-group">
                        <span class="input-icon">🆔</span>
                        <input type="text" v-model="dni" placeholder="DNI para validar" required :disabled="isProcessing" maxlength="15"/>
                    </div>
                    
                    <div v-if="message" class="error-message">⚠️ {{ message }}</div>

                    <button type="submit" class="btn-primary" :disabled="isProcessing">
                        {{ isProcessing ? 'Validando...' : 'VALIDAR DATOS' }}
                    </button>
                    <button type="button" class="btn-cancel" @click="goToLogin">Volver al Login</button>
                </form>

                <div v-if="step === 2">
                    <p class="result-label success-message">✅ Validación exitosa para **{{ usernameFound }}**</p>
                    
                    <p class="instruction large-instruction">
                        Por motivos de seguridad, su contraseña anterior no puede ser mostrada.
                        Proceda a **establecer una nueva clave** para recuperar el acceso.
                    </p>
                    
                    <div class="action-options">
                        <button type="button" class="btn-secondary" @click="goToLogin">
                            Volver al Login (Sin cambiar clave)
                        </button>
                        <button type="button" class="btn-warning" @click="step = 3">
                            ESTABLECER NUEVA CONTRASEÑA
                        </button>
                    </div>
                </div>

                <form @submit.prevent="handlePasswordReset" v-if="step === 3">
                    <p class="instruction">Paso 2: Ingrese su nueva contraseña.</p>
                    
                    <div class="input-group">
                        <span class="input-icon">🔑</span>
                        <input type="password" v-model="newPassword" placeholder="Nueva Contraseña" required minlength="6" :disabled="isProcessing"/>
                    </div>

                    <div class="input-group">
                        <span class="input-icon">🔒</span>
                        <input type="password" v-model="confirmPassword" placeholder="Confirmar Nueva Contraseña" required :disabled="isProcessing"/>
                    </div>
                    
                    <div v-if="message" class="error-message">⚠️ {{ message }}</div>

                    <button type="submit" class="btn-primary" :disabled="isProcessing">
                        {{ isProcessing ? 'Encriptando...' : 'GUARDAR Y VOLVER AL LOGIN' }}
                    </button>
                    <button type="button" class="btn-cancel" @click="goToLogin">Cancelar</button>
                </form>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* REUTILIZANDO ESTILOS BASE DE LOGINVIEW.VUE */
.login-page { height: 100vh; width: 100%; display: flex; justify-content: center; align-items: center; position: relative; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; overflow: hidden; }
.background-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: url('https://images.unsplash.com/photo-1497294815431-9365093b7331?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80') no-repeat center center/cover; box-shadow: inset 0 0 0 1000px rgba(15, 23, 42, 0.85); z-index: 1; filter: blur(2px); }
.login-wrapper { position: relative; z-index: 10; width: 100%; max-width: 500px; padding: 20px; }
.login-card { background: white; border-radius: 16px; padding: 40px 30px; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3); text-align: center; min-height: 500px; display: flex; flex-direction: column; justify-content: center; }
.brand-header { margin-bottom: 30px; }
.brand-header h1 { font-size: 1.4rem; color: #1e293b; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
.subtitle { color: #64748b; font-size: 0.75rem; font-weight: 600; margin-top: 5px; letter-spacing: 1px; }
.input-group { position: relative; margin-bottom: 20px; }
.input-icon { position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 1.1rem; }
.input-group input { width: 85%; padding: 14px 15px 14px 45px; border: 2px solid #f1f5f9; background-color: #f8fafc; border-radius: 8px; font-size: 0.95rem; color: #334155; transition: all 0.3s; outline: none; }
.input-group input:focus { border-color: #3b82f6; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1); }
.btn-primary { width: 100%; padding: 14px; background: #3b82f6; color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 700; cursor: pointer; margin-top: 10px; transition: 0.2s;}
.error-message { color: #ef4444; background-color: #fef2f2; padding: 10px; border-radius: 6px; font-size: 0.85rem; margin-top: 15px; border: 1px solid #fecaca; }

/* Estilos de Recuperación Específicos */
.instruction { color: #475569; font-size: 0.95rem; font-weight: 600; margin-bottom: 20px; text-align: left; }
.large-instruction { color: #1e293b; font-size: 1rem; font-weight: 500; margin-bottom: 25px; }
.btn-cancel { width: 100%; margin-top: 10px; padding: 14px; background: #e2e8f0; color: #475569; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s;}
.btn-cancel:hover { background: #cbd5e1; }
.result-label { color: #475569; font-size: 0.95rem; font-weight: 600; margin-top: 10px; }
.action-options { display: flex; justify-content: space-between; gap: 10px; margin-top: 30px;}
.action-options button { width: 50%; padding: 12px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: 0.2s; }
.btn-secondary { background: #f8fafc; color: #475569; border: 1px solid #cbd5e1; }
.btn-warning { background: #f97316; color: white; border: none; }
.success-message { background: #dcfce7; color: #16a34a; padding: 10px; border-radius: 8px; font-weight: 700; text-align: center; }
</style>