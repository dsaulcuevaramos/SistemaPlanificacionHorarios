// src/api/docenteMock.js
import axios from 'axios';

// Configura la URL base de tu FastAPI
const API_URL = 'http://127.0.0.1:8000/api/v1';

// Función auxiliar para obtener el token
const getHeader = () => {
  const token = localStorage.getItem('token');
  return { headers: { Authorization: `Bearer ${token}` } };
};

export default {
  async getAll() {
    // GET /docentes/ (Tu backend filtra por escuela automáticamente)
    const response = await axios.get(`${API_URL}/docentes/`, getHeader());
    return response.data;
  },

  async create(data) {
    // POST /docentes/
    const response = await axios.post(`${API_URL}/docentes/`, data, getHeader());
    return response.data;
  },

  async update(id, data) {
    // PUT /docentes/{id}
    const response = await axios.put(`${API_URL}/docentes/${id}`, data, getHeader());
    return response.data;
  },

  // Simulación de "Delete" lógico (cambiar estado) si tu backend lo soporta,
  // o update simple del campo estado.
  async toggleEstado(id, nuevoEstado) {
    // Usamos el update parcial o full según tu backend
    // Asumimos que tu endpoint update soporta enviar solo el estado
    return await this.update(id, { estado: nuevoEstado }); 
  }
};