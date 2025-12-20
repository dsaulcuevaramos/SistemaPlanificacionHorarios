import api from './axios';

const ENDPOINT_GESTION = '/gestion_horarios';
const ENDPOINT_HORARIOS = '/horarios';

export default {
    // --- BLOQUES (LA REJILLA) ---
    async getBloquesByTurno(idTurno) {
        const response = await api.get(`${ENDPOINT_GESTION}/bloques/turno/${idTurno}`);
        return response.data;
    },

    // --- GRUPOS Y SESIONES (LA CARGA) ---
    async getGruposByPeriodo(idPeriodo) {
        const response = await api.get(`${ENDPOINT_GESTION}/grupos/periodo/${idPeriodo}`);
        return response.data;
    },

    // --- EL HORARIO FINAL ---
    async getHorarioCompleto(idPeriodo) {
        const response = await api.get(`${ENDPOINT_HORARIOS}/periodo/${idPeriodo}`);
        return response.data;
    },

    async asignarSesion(payload) {
        // payload: { id_sesion, id_bloque, id_aula, id_periodo }
        const response = await api.post(`${ENDPOINT_HORARIOS}/`, payload);
        return response.data;
    },

    async validarCruce(idDocente, idBloque) {
        const response = await api.post(`${ENDPOINT_GESTION}/validar-cruce`, {
            id_docente: idDocente,
            id_bloque: idBloque
        });
        return response.data;
    }
};