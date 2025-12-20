import api from './axios'; 
const ENDPOINT = '/periodos';

const getAll = async () => {
    try {
        const response = await api.get(ENDPOINT + '/'); // Ojo con el slash, usa el que te funcione
        return response.data;
    } catch (error) {
        console.error("Error al listar periodos:", error);
        throw error;
    }
};

// --- AGREGA ESTO ---
const getById = async (id) => {
    try {
        const response = await api.get(`${ENDPOINT}/${id}`);
        return response.data;
    } catch (error) {
        console.error("Error al obtener periodo:", error);
        throw error;
    }
};

const create = async (periodoData) => {
    try {
        const response = await api.post(ENDPOINT + '/', periodoData);
        return response.data;
    } catch (error) {
        console.error("Error al crear:", error);
        throw error;
    }
};

const update = async (id, periodoData) => {
    try {
        const response = await api.put(`${ENDPOINT}/${id}`, periodoData);
        return response.data;
    } catch (error) {
        console.error("Error al actualizar:", error);
        throw error;
    }
};

export default {
    getAll,
    getById, // <--- NO OLVIDES EXPORTARLO
    create,
    update
};