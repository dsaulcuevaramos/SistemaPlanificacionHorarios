import { defineStore } from 'pinia';
import api from '../api/axios';
import router from '../router';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('token') || null,
        // Si hay basura en el localStorage, lo ignoramos para evitar errores
        user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null,
        loading: false,
        error: null
    }),
    
    getters: {
        isAuthenticated: (state) => !!state.token
    },

    actions: {
        // --- Acción para obtener los datos reales del usuario ---
        // Tienes que buscar en tu Swagger (http://localhost:8000/docs) cuál es la ruta correcta
        // Posibles opciones: '/auth/me', '/api/v1/me', '/users/profile'
        async fetchCurrentUser() {
            try {
                // CAMBIO AQUÍ: Usamos la ruta bajo 'usuarios'
                // Si tu router en python tiene prefix="/usuarios", entonces es:
                const response = await api.get('/usuarios/me'); 
                
                this.user = response.data;
                localStorage.setItem('user', JSON.stringify(this.user));
            } catch (error) {
                console.error("Error cargando perfil:", error);
                // Opcional: si falla mucho, logout
            }
        },

    
        async recoverPassword(usernameOrEmail, dni) {
            this.loading = true;
            this.error = null;
            try {
                const response = await api.post('/auth/recover-password', {
                    username_or_email: usernameOrEmail,
                    dni: dni
                });
                return response.data;
            } catch (err) {
                const msg = err.response?.data?.detail || "Error de validación.";
                this.error = msg;
                throw msg;
            } finally {
                this.loading = false;
            }
        },

        async resetPassword(usernameOrEmail, dni, newPassword) {
            this.loading = true;
            this.error = null;
            try {
                const response = await api.post('/auth/reset-password', {
                    username_or_email: usernameOrEmail,
                    dni: dni,
                    new_password: newPassword
                });
                return response.data;
            } catch (err) {
                const msg = err.response?.data?.detail || "Error al cambiar contraseña.";
                this.error = msg;
                throw msg;
            } finally {
                this.loading = false;
            }
        },

        async login(username, password) {
            this.loading = true; 
            this.error = null;
            try {
                const formData = new FormData();
                formData.append('username', username);
                formData.append('password', password);

                const response = await api.post('/auth/login', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
                
                // --- DEBUG: MIRA ESTO EN CONSOLA ---
                console.log("🔥 RESPUESTA DEL BACKEND AL LOGIN:", response.data);

                // 1. Guardar Token
                this.token = response.data.access_token;
                localStorage.setItem('token', this.token);

                // 2. Intentar sacar el usuario de la respuesta del login
                if (response.data.user) {
                    this.user = response.data.user;
                    localStorage.setItem('user', JSON.stringify(this.user));
                } 
                // 3. Si no viene el usuario, intentamos pedirlo aparte (pero protegemos el error)
                else {
                    // Creamos un usuario temporal para que no falle el frontend
                    this.user = { username: username, id_escuela: null }; 
                    
                    // Intentamos buscar los datos reales sin bloquear el flujo
                    await this.fetchCurrentUser();
                }
                
                return true; 
                
            } catch (err) {
                console.error("Error Store Login:", err);
                const msg = err.response?.data?.detail || "Error de conexión o credenciales inválidas.";
                this.error = msg;
                throw msg;
            } finally {
                this.loading = false;
            }
        },

        logout() {
            this.token = null;
            this.user = null;
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            router.push('/login'); 
        }
    }
});