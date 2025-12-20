import api from './axios'; // Tu instancia configurada de axios

const ENDPOINT = '/contratos';

export default {
    /**
     * Obtiene la lista de docentes que ya están asignados a un periodo específico.
     * Sirve para la "sincronización" en la vista.
     */
    async getDisponibilidadByPeriodo(idPeriodo) {
        try {
            const response = await api.get(`${ENDPOINT}/disponibilidad/periodo/${idPeriodo}`);
            return response.data;
        } catch (error) {
            console.error("Error al obtener disponibilidad:", error);
            throw error;
        }
    },

    /**
     * Envía los datos para crear el Contrato y la Disponibilidad en una sola operación.
     * El payload debe contener: id_docente, id_periodo, fecha_inicio, fecha_fin, 
     * horas_tope_semanales y turnos_preferidos.
     */
    async asignarDocenteAPeriodo(payload) {
        try {
            const response = await api.post(`${ENDPOINT}/asignar-periodo`, payload);
            return response.data;
        } catch (error) {
            console.error("Error al asignar docente:", error.response?.data?.detail || error.message);
            throw error;
        }
    },

    async quitarContrato(idPeriodo, idDocente) {
    const response = await api.delete(`${ENDPOINT}/quitar-contrato/${idPeriodo}/${idDocente}`);
    return response.data;
}
};

