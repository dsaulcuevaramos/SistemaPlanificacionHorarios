import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/v1', // Ajusta tu base URL si es diferente
    //baseURL: 'http://5.161.126.165:8000/api/v1', // Ajusta tu base URL si es diferente
    headers: {
        'Accept': 'application/json',       // 'Content-Type': 'multipart/form-data'
    }
});


// Interceptor: Antes de cada petición, inyecta el Token
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, error => {
    return Promise.reject(error);
});

// Interceptor: Si el token expira (Error 401), limpia y redirige
api.interceptors.response.use(
    response => response,
    error => {
        const status = error.response ? error.response.status : null;
        const requestUrl = error.config.url;

        // **CRÍTICO:** Solo redirigimos si el 401 NO es en la URL de Login.
        const isLoginUrl = requestUrl && requestUrl.includes('/auth/login'); //const isLoginUrl = requestUrl.includes('/auth/login');
        
        if (status === 401 && !isLoginUrl) {
            // Error 401 en cualquier OTRA URL (token expirado)
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            // Forzamos la redirección para limpiar el estado de la aplicación
            window.location.href = '/login'; 
            return Promise.reject(error); 
        }
        
        // Error 401/400 del Login pasa al catch de la vista de Login.
        return Promise.reject(error);
    }
);

export default api;