import api from './axios'
const ENDPOINT = '/aulas'

const getAll = async() => {
    try{
        const response = await api.get(ENDPOINT + '/');
        return response.data;
    }catch (error) {
        console.error("Error al listar aulas", error)
        throw error;
    }
};

const create = async(aulaData) => {
    try{
        const response = await api.post(ENDPOINT + '/', aulaData)
        return response.data;
    }catch (error) {
        console.error("Error al crear aulas:", error.response?.data?.detail || error.message);
        throw error;
    }
};

const update = async(id, aulaData) =>{
    try{
        const response = await api.put(`${ENDPOINT}/${id}`, aulaData);
        return response.data;
    } catch (error) {
        console.error("Error al actualizar aula:", error.response?.data?.detail || error.message);
        throw error;
    }
};

const toggleStatus = async (id, aulaData) => {
    return await update(id, aulaData);
}

const remove = async (id) => {
    //esto es para eliminado fisico
}

export default{
    getAll,
    create,
    update,
    toggleStatus,
    remove
};