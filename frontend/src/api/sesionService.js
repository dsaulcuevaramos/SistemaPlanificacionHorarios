import api from './axios';

const ENDPOINT = '/horarios/sesiones';

export default {
    async getByGrupo(idGrupo) {
        const response = await api.get(`${ENDPOINT}/grupo/${idGrupo}`);
        return response.data;
    },
    
    async generarAutomatico(idGrupo) {
        const response = await api.post(`${ENDPOINT}/generar-automatico/${idGrupo}`);
        return response.data;
    }
};