import api from './axios';

const ENDPOINT_HORARIOS = '/horarios';

export default {
    // --- BLOQUES (LA REJILLA) ---
    async getBloquesByTurno(idTurno) {
        const response = await api.get(`${ENDPOINT_HORARIOS}/bloques/turno/${idTurno}`);
        return response.data;
    },

    // --- GRUPOS Y SESIONES (LA CARGA) ---
    async getGruposByPeriodo(idPeriodo) {
        const response = await api.get(`${ENDPOINT_HORARIOS}/grupos/periodo/${idPeriodo}`);
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
        const response = await api.post(`${ENDPOINT_HORARIOS}/validar-cruce`, {
            id_docente: idDocente,
            id_bloque: idBloque
        });
        return response.data;
    },

    
    // Obtener sesiones que aún no tienen horario asignado
    async getSesionesPendientes(idPeriodo) {
        const response = await api.get(`${ENDPOINT_HORARIOS}/sesiones/pendientes/${idPeriodo}`);
        return response.data;
    },


    async getByAula(idPeriodo, idAula) {
        const response = await api.get(`${ENDPOINT_HORARIOS}/periodo/${idPeriodo}/aula/${idAula}`);
        return response.data;
    },



    // Guardar una nueva asignación
    async asignar(payload) {
        // OJO AQUÍ: Debe decir /asignar al final
        const response = await api.post(`${ENDPOINT_HORARIOS}/guardar-asignacion`, payload);
        return response.data;
    },

    // Eliminar una asignación
    async eliminar(idHorario) {
        await api.delete(`${ENDPOINT_HORARIOS}/${idHorario}`);
    },

    async onDrop(event, bloque, dia) {
        const sesionData = JSON.parse(event.dataTransfer.getData('sesion'));
        
        // Validar localmente o llamar al endpoint de validación
        const error = await horarioService.validarChoque({
            id_sesion: sesionData.id,
            id_bloque: bloque.id,
            dia: dia,
            id_aula: idAulaSeleccionada.value
        });

        if (!error) {
            // Se agrega a la rejilla visual (todavía no a la DB si prefieres modo borrador)
            this.renderizarSesion(sesionData, bloque, dia);
        } else {
            Swal.fire('¡Cuidado!', error, 'error');
        }
    },


    async autogenerar(idPeriodo, ciclo) {
        return api.post(`${ENDPOINT_HORARIOS}/autogenerar-ciclo/${idPeriodo}/${ciclo}`);
    },

    async descargarReporteExcel(idPeriodo) {
        return api.get(`${ENDPOINT_HORARIOS}/exportar-excel/${idPeriodo}`, {
            responseType: 'blob' 
        });
    }

};