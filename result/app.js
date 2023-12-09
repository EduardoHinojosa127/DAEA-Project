const express = require('express');
const mongoose = require('mongoose');
const path = require('path');
const axios = require('axios');

const app = express();
const port = 3001;
app.use(express.urlencoded({ extended: true }));
// Conexión a MongoDB
mongoose.connect('mongodb://mongo:27017/DAEA11', { useNewUrlParser: true, useUnifiedTopology: true });

// Definición del esquema de la colección
  const movieScoreSchema = new mongoose.Schema({
    usuario: String,
    pelicula1: String,
    pelicula2: String,
    pelicula3: String,
    pelicula4: String,
    pelicula5: String,
  });

  const MovieScore = mongoose.model('MovieScore', movieScoreSchema);

  // Ruta para la página principal
  app.get('/', async (req, res) => {
    try {
      // Obtén los datos de MongoDB
      const db = mongoose.connection.db;
      const collection = db.collection('movie_scores');
      const movieScores = await collection.find({}, { _id: 0, __v: 0 }).toArray();

      // Renderiza la página y pasa los datos como contexto
      res.render('index', { movieScores, respuesta: undefined });
    } catch (error) {
      console.error(error);
      res.status(500).send('Error interno del servidor');
    }
  });

  // ... (código anterior)

// Ruta para manejar la solicitud POST desde el cliente
app.post('/enviar-datos', async (req, res) => {
  try {
    // Obtén los datos del formulario enviado por el cliente
    const datosFormulario = req.body;
    // Buscar el usuario en la base de datos
    const db = mongoose.connection.db;
    const collection = db.collection('movie_scores');
    const movieScores = await collection.find({}, { _id: 0, __v: 0 }).toArray();
    const usuarioEncontrado = await collection.find({usuario: datosFormulario.user1}, { _id: 0, __v: 0 }).toArray();

    console.log(datosFormulario.user1) 
    console.log(usuarioEncontrado[0])

    if (usuarioEncontrado) {
      
      const startTime = new Date();
      const respuestaAPI = await axios.post('http://flask-container:5000/procesar', usuarioEncontrado[0]);
  
      // Obtén la fecha y hora de finalización
      const endTime = new Date();

      // Calcula el tiempo de ejecución en milisegundos
      const executionTimeInMilliseconds = endTime - startTime;

      // Imprime el tiempo de ejecución
      console.log(`Tiempo de ejecución del POST: ${executionTimeInMilliseconds} ms`);

      // Manejar la respuesta de la API según sea necesario
      console.log('Respuesta del servidor:', respuestaAPI.data);
      const respuesta = respuestaAPI.data
      console.log(respuesta.usuario_recibido)
      res.render('index', { respuesta, movieScores });

    } else {
      console.log('Usuario no encontrado. Valor buscado:', datosFormulario.user1);
      res.status(404).json({ error: 'Usuario no encontrado' });
      
      res.render('index', { respuesta: undefined });
    }

  } catch (error) {
    // Manejar los errores de la solicitud
    console.error('Error al enviar datos:', error);
    res.status(500).json({ error: 'Error en el servidor' });
  }
});

// ... (código posterior)


  // Configuración de la vista y el directorio público
  app.set('views', path.join(__dirname, 'views'));
  app.set('view engine', 'ejs'); // Puedes usar otro motor de plantillas si prefieres

  // Iniciar el servidor
  app.listen(port, () => {
    console.log(`Servidor iniciado en http://localhost:${port}`);
  });

