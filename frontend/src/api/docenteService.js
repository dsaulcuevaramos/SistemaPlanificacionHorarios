import api from './axios'; // Importa la instancia de Axios configurada

const ENDPOINT = '/docentes'; // El prefijo de tu API FastAPI es /api/v1/docentes

// 1. OBTENER TODOS LOS DOCENTES (LISTAR)
const getAll = async () => {
    try {
        const response = await api.get(ENDPOINT + '/');
        // El backend devuelve automáticamente los docentes de la escuela del usuario
        // debido a la lógica de get_current_user.
        return response.data; 
    } catch (error) {
        console.error("Error al listar docentes:", error);
        throw error;
    }
};

// 2. CREAR NUEVO DOCENTE
const create = async (docenteData) => {
    try {
        // DocenteData debe incluir id_escuela, dni, nombre, etc.
        const response = await api.post(ENDPOINT + '/', docenteData);
        return response.data;
    } catch (error) {
        console.error("Error al crear docente:", error.response?.data?.detail || error.message);
        throw error;
    }
};

// 3. ACTUALIZAR DOCENTE
const update = async (id, docenteData) => {
    try {
        const response = await api.put(`${ENDPOINT}/${id}`, docenteData);
        return response.data;
    } catch (error) {
        console.error("Error al actualizar docente:", error.response?.data?.detail || error.message);
        throw error;
    }
};

// 4. CAMBIAR ESTADO (Activar/Desactivar)
// En nuestra arquitectura, usamos el mismo endpoint de PUT para cambiar el estado.
const toggleStatus = async (id, docenteData) => {
    // El backend espera el objeto completo con el nuevo estado.
    return await update(id, docenteData); 
};

// BORRADO LOGICO (no creo que sea necesario)
const remove = async (id) => {
    /*
    try{
        const response = await api.post(`${ENDPOINT}/${id}`, id)
        return response.data; // return true
    }catch (error) {
        console.error("Error al eliminar docente:", error.response?.data?.detail || error.message);
        throw error;
    }
    */
};


export default {
    getAll,
    create,
    update,
    toggleStatus,
    remove
};

