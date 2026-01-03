import api from './axios'; // Asegúrate de que apunte a tu configuración de axios

const ENDPOINT = '/grupos';

export default {
    // 1. Obtener todos los grupos (CRUD básico)
    async getAll() {
        const response = await api.get(ENDPOINT);
        return response.data;
    },

    // 2. Obtener los "Ciclos" disponibles en un periodo
    // (Ej: Devuelve [{id: 1, nombre: 'Ciclo I'}, {id: 2, nombre: 'Ciclo II'}])
    async getCiclosByPeriodo(idPeriodo) {
        const response = await api.get(`${ENDPOINT}/periodo/${idPeriodo}/ciclos`);
        return response.data;
    },

    // 3. Obtener los Grupos específicos de un ciclo en ese periodo
    // (Ej: Devuelve Grupo A, Grupo B del Ciclo I)
    async getGruposByCiclo(idCiclo, idPeriodo) {
        // Nota: A veces el ciclo es solo un número, o un ID. 
        // Ajusta la URL según cómo definamos el backend abajo.
        const response = await api.get(`${ENDPOINT}/ciclo/${idCiclo}`);
        return response.data;
    },

    // 4. Obtener detalle de un grupo (para saber su turno, etc.)
    async getById(id) {
        const response = await api.get(`${ENDPOINT}/${id}`);
        return response.data;
    },
    async getCursosConGrupos(idPeriodo) {
        const response = await api.get(`${ENDPOINT}/periodo/${idPeriodo}/detallado`);
        return response.data;
    },

    // Crear grupos (A, B, C)
    async crearLote(payload) {
        // payload: { id_curso_aperturado, id_docente, id_turno, cantidad_grupos, vacantes }
        const response = await api.post(`${ENDPOINT}/generar-lote`, payload);
        return response.data;
    },

    async update(id, datos) {
        return api.put(`${ENDPOINT}/${id}`, datos); // Ajusta la URL a tu backend
    },

    // Borrar
    async eliminar(idGrupo) {
        await api.delete(`${ENDPOINT}/${idGrupo}`);
    }
};
