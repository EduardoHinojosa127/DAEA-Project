const express = require('express');
const redis = require('redis');

const app = express();
const port = 3000;

app.use(express.json());
app.use(express.static(__dirname));
app.use(express.urlencoded({ extended: true }));

// Configuración de la conexión a Redis
const redisClient = redis.createClient({
  host: 'redis-server', // Reemplaza con la dirección IP de tu instancia de EC2
  port: 6379 // Reemplaza con el puerto que hayas elegido al ejecutar el contenedor de Redis
});

redisClient.on('connect', () => {
  console.log('Conectado a Redis');
});

redisClient.on('error', (err) => {
  console.error(`Error de conexión a Redis: ${err}`);
});

// Configuración de Express para el manejo de datos JSON y archivos estáticos
app.use(express.json());
app.use(express.static(__dirname));

// Ruta para mostrar el formulario de valoración
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

// Ruta para manejar las valoraciones enviadas por el formulario
app.post('/valorar', (req, res) => {
  const { usuario, pelicula1, pelicula2, pelicula3, pelicula4, pelicula5 } = req.body;

  // Agrega registros de consola para imprimir el contenido del JSON
  console.log('JSON recibido:', req.body);

  // Guardar las valoraciones en Redis
  redisClient.hmset(usuario, {
    'pelicula1': pelicula1,
    'pelicula2': pelicula2,
    'pelicula3': pelicula3,
    'pelicula4': pelicula4,
    'pelicula5': pelicula5
  }, (err) => {
    if (err) {
      console.error(`Error al guardar las valoraciones en Redis: ${err}`);
      res.status(500).send('Error interno del servidor');
    } else {
      redisClient.publish('nuevosDatos', usuario);
      res.status(200).send('Valoraciones guardadas correctamente en Redis');
    }
  });
});

// Iniciar el servidor
app.listen(port, () => {
  console.log(`Servidor iniciado en http://localhost:${port}`);
});
