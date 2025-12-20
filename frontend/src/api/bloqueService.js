import api from './axios';

const ENDPOINT = '/gestion_horarios';

export default {
    // Obtener bloques de un turno específico
    async getByTurno(idTurno) {
        const response = await api.get(`${ENDPOINT}/bloques/turno/${idTurno}`);
        return response.data;
    },

    // Crear un bloque (id_turno, dia_semana, hora_inicio, hora_fin, orden)
    async create(bloqueData) {
        const response = await api.post(`${ENDPOINT}/bloques/`, bloqueData);
        return response.data;
    },

    // Eliminar un bloque
    async remove(id) {
        const response = await api.delete(`${ENDPOINT}/bloques/${id}`);
        return response.data;
    },

    // Generación masiva (Opcional: para no crear uno por uno)
    async generarAutomatico(payload) {
        return await api.post(`${ENDPOINT}/bloques/generar`, payload);
    }
};