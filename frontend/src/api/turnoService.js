import api from './axios'; // Tu instancia configurada con interceptores

const ENDPOINT = '/turnos';

/*
// Obtener turnos por ID de Versión
const getByVersion = async (versionId) => {
    try {
        // Asumiendo que en el backend la ruta es: GET /turnos/version/{id}
        const response = await api.get(`${ENDPOINT}/version/${versionId}`);
        return response.data;
    } catch (error) {
        console.error("Error al obtener turnos de la versión:", error);
        throw error;
    }};
// Crear un nuevo turno
const create = async (turnoData) => {
    try {
        // turnoData debe incluir: nombre, hora_inicio, hora_fin, version_id
        const response = await api.post(ENDPOINT + '/', turnoData);
        return response.data;
    } catch (error) {
        // Manejo de error consistente con tu servicio de cursos
        console.error("Error al crear turno:", error.response?.data?.detail || error.message);
        throw error;
    }};
// Eliminar un turno
const remove = async (id) => {
    try {
        const response = await api.delete(`${ENDPOINT}/${id}`);
        return response.data;
    } catch (error) {
        console.error("Error al eliminar turno:", error.response?.data?.detail || error.message);
        throw error;
    }}
export default {getByVersion,create,remove};
*/

export default {
    // Ya no recibe parámetros, el backend filtra por tu token (usuario -> escuela)
    async getAll() {
        const response = await api.get(ENDPOINT + '/');
        return response.data;
    },

    async create(turnoData) {
        // turnoData ya NO lleva version_id
        const response = await api.post(ENDPOINT + '/', turnoData);
        return response.data;
    },
    
    // ... update, remove igual que antes ...
    async update(id, data) { return (await api.put(`${ENDPOINT}/${id}`, data)).data; },
    async toggleStatus(id, data) { return this.update(id, data); },
    async remove(id) { return (await api.delete(`${ENDPOINT}/${id}`)).data; }
};