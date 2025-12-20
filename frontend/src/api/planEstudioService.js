import api from './axios';

const ENDPOINT_PLANES = '/planes'; 
const ENDPOINT_VERSIONES = '/versiones'; 

// --- PLANES DE ESTUDIO (Nivel Superior) ---

// 1. OBTENER TODOS LOS PLANES (LISTAR)
const getAllPlanes = async () => {
    try {
        const response = await api.get(ENDPOINT_PLANES + '/');
        // El backend debe filtrar por id_escuela del usuario
        return response.data; 
    } catch (error) {
        throw error;
    }
};

// 2. CREAR NUEVO PLAN
const createPlan = async (planData) => {
    try {
        const response = await api.post(ENDPOINT_PLANES + '/', planData);
        return response.data;
    } catch (error) {
        throw error;
    }
};

// 3. ACTUALIZAR PLAN (Incluye cambiar estado: activo/inactivo)
const updatePlan = async (id, planData) => {
    try {
        const response = await api.put(`${ENDPOINT_PLANES}/${id}`, planData);
        return response.data;
    } catch (error) {
        throw error;
    }
};


// --- VERSIONES DEL PLAN (Nivel Detalle) ---

// 4. OBTENER VERSIONES POR ID DE PLAN
// Lo usarás al expandir un plan. Asumimos que tu backend soporta el filtro GET /versiones?id_plan=X
const getAllVersionesByPlan = async (idPlan) => {
    try {
        const response = await api.get(`${ENDPOINT_VERSIONES}/?id_plan=${idPlan}`);
        return response.data; 
    } catch (error) {
        throw error;
    }
};

// 5. CREAR NUEVA VERSIÓN
const createVersion = async (versionData) => {
    // versionData debe incluir id_plan_estudio
    try {
        const response = await api.post(ENDPOINT_VERSIONES + '/', versionData);
        return response.data;
    } catch (error) {
        throw error;
    }
};

// 6. ACTUALIZAR VERSIÓN (Incluye cambiar estado)
const updateVersion = async (id, versionData) => {
    try {
        const response = await api.put(`${ENDPOINT_VERSIONES}/${id}`, versionData);
        return response.data;
    } catch (error) {
        throw error;
    }
};


export default {
    getAllPlanes,
    createPlan,
    updatePlan,
    
    getAllVersionesByPlan,
    createVersion,
    updateVersion
};