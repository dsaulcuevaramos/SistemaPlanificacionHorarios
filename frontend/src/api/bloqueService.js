import api from './axios';

const ENDPOINT = '/horarios';

export default {
    async getByTurno(idTurno) {
        const response = await api.get(`${ENDPOINT}/bloques/turno/${idTurno}`);
        return response.data;
    },

    // Envía la lista de días y la lista de intervalos (inicio, fin, orden)
    async createMasivo(payload) {
        // payload: { id_turno, dias: [], intervalos: [] }
        const response = await api.post(`${ENDPOINT}/bloques/masivo`, payload);
        return response.data;
    },

    async removeAllByTurno(idTurno) {
        const response = await api.delete(`${ENDPOINT}/bloques/turno/${idTurno}`);
        return response.data;
    },

    async remove(id) {
        const response = await api.delete(`${ENDPOINT}/bloques/${id}`);
        return response.data;
    }
    
};