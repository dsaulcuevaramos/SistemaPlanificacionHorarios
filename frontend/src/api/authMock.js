// src/api/authMock.js
export default {
  async login(username, password) {
    return new Promise((resolve, reject) => {
      // Simulamos un retraso de red (como si fuera a internet)
      setTimeout(() => {
        // CREDENCIALES QUEMADAS PARA PRUEBAS
        if (username === 'admin' && password === '123456') {
          resolve({
            id: 1,
            username: 'admin',
            nombre: 'Diego Cueva',
            rol: 'ADMINISTRADOR',
            token: 'token-falso-seguro-123'
          });
        } else {
          reject(new Error('Credenciales incorrectas'));
        }
      }, 800);
    });
  }
};


