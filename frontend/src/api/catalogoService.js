import api from './axios';

// CRÍTICO: Usaremos el endpoint que proporcionaste
const ENDPOINT = '/catalogo';

const getByTableName = async (tableName) => {
    try {
        // 1. Obtener TODOS los registros del catálogo
        const response = await api.get(ENDPOINT + '/');
        const allCatalogItems = response.data;
        
        // 2. Filtrar los resultados localmente por nombre_tabla
        const filteredItems = allCatalogItems.filter(item => 
            item.nombre_tabla === tableName.toUpperCase() // Aseguramos mayúsculas para la comparación
        );
        
        return filteredItems;

    } catch (error) {
        console.error(`Error al cargar la tabla ${tableName} desde /catalogo/:`, error);
        throw error;
    }
};


// CRÍTICO: Función adicional para obtener todo el catálogo sin filtrar, si fuera necesario
const getAllCatalog = async () => {
    try {
        const response = await api.get(ENDPOINT + '/');
        return response.data;
    } catch (error) {
        console.error("Error al cargar el catálogo completo:", error);
        throw error;
    }
};


export default {
    getByTableName,
    getAllCatalog
};