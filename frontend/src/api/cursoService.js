import api from './axios'; // Importa la instancia de Axios configurada

const ENDPOINT = '/cursos';

const getAll = async () => {
    try {
        // La lista de cursos NO necesita un filtro de plan aquí,
        // ya que el filtro se hace en la vista. Solo obtenemos todos los cursos de la escuela.
        const response = await api.get(ENDPOINT + '/');
        return response.data;
    } catch (error) {
        console.error("Error al listar cursos:", error);
        throw error;
    }
};

const create = async (cursoData) => {
    try {
        // cursoData debe incluir id_plan e id_escuela (aunque id_escuela es opcional si el backend lo deduce)
        const response = await api.post(ENDPOINT + '/', cursoData);
        return response.data;
    } catch (error) {
        console.error("Error al crear curso:", error.response?.data?.detail || error.message);
        throw error;
    }
};

const update = async (id, cursoData) => {
    try {
        const response = await api.put(`${ENDPOINT}/${id}`, cursoData);
        return response.data;
    } catch (error) {
        console.error("Error al actualizar curso:", error.response?.data?.detail || error.message);
        throw error;
    }
};

// 4. CAMBIAR ESTADO (Activar/Desactivar)
// En nuestra arquitectura, usamos el mismo endpoint de PUT para cambiar el estado.
const toggleStatus = async (id, crusoData) => {
    // El backend espera el objeto completo con el nuevo estado.
    return await update(id, crusoData);
};

// 5. BORRAR DOCENTE (Si fuera necesario)
const remove = async (id) => {
    // Si tu backend tiene un endpoint DELETE
    // try {
    //     await api.delete(`${ENDPOINT}/${id}`);
    //     return true;
    // } catch (error) {
    //     throw error;
    // }
};




//para los requisitos 
const addRequisito = async (idCurso, idRequisito, idPlanVersion) => {
    // Nota: enviamos id_plan_version como query param para simplificar
    const response = await api.post(`${ENDPOINT}/${idCurso}/requisitos/${idRequisito}?id_plan_version=${idPlanVersion}`);
    return response.data;
};
const removeRequisito = async (idCurso, idRequisito) => {
    const response = await api.delete(`${ENDPOINT}/${idCurso}/requisitos/${idRequisito}`);
    return response.data;
};

export default {
    getAll,
    create,
    update,
    toggleStatus,
    remove,

    addRequisito,
    removeRequisito
};