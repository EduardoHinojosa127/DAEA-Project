using System;
using StackExchange.Redis;
using MongoDB.Driver;
using MongoDB.Bson;

class Program
{
    static void Main()
    {
        Console.WriteLine("Worker iniciado...");

        // Configura la conexión a Redis
        var redisConnectionString = "redis-server:6379,abortConnect=false"; // Reemplaza con la IP y el puerto correctos
        var redis = ConnectionMultiplexer.Connect(redisConnectionString);

        // Configura el suscriptor de Redis para escuchar la señal
        var subscriber = redis.GetSubscriber();
        subscriber.Subscribe("nuevosDatos", (channel, message) =>
        {
            Console.WriteLine($"Se recibió una señal para el usuario: {message}");

            // Lógica para buscar en Redis y guardar en MongoDB
            BuscarEnRedisYGuardarEnMongoDB(message);
        });

        // Mantén la aplicación en ejecución para escuchar las señales
        Console.WriteLine("Esperando señales...");
        Console.ReadLine();
	while (true)
        {
            // Puedes agregar lógica adicional aquí si es necesario
            // ...

            // Espera un breve período antes de volver a verificar
            System.Threading.Thread.Sleep(1000);
        }
    }

    static void BuscarEnRedisYGuardarEnMongoDB(string usuario)
    {
	Console.WriteLine("entro a funcion");
        // Configura la conexión a MongoDB local
        var mongoConnectionString = "mongodb://mongo:27017";
        var mongoClient = new MongoClient(mongoConnectionString);
        var database = mongoClient.GetDatabase("DAEA11");
        var collection = database.GetCollection<BsonDocument>("movie_scores");

        // Configura la conexión a Redis
        var redisConnectionString = "redis-server:6379"; // Reemplaza con la IP y el puerto correctos
        var redis = ConnectionMultiplexer.Connect(redisConnectionString);
        var redisDatabase = redis.GetDatabase();

        // Obtener valores para las tres películas
        var pelicula1 = redisDatabase.HashGet(usuario, "pelicula1");
        var pelicula2 = redisDatabase.HashGet(usuario, "pelicula2");
        var pelicula3 = redisDatabase.HashGet(usuario, "pelicula3");
        var pelicula4 = redisDatabase.HashGet(usuario, "pelicula4");
        var pelicula5 = redisDatabase.HashGet(usuario, "pelicula5");

        // Crear el filtro para buscar el documento existente por usuario
        var filter = Builders<BsonDocument>.Filter.Eq("usuario", usuario);

        // Crear el documento BSON
        var document = new BsonDocument
        {
            { "usuario", usuario },
            { "pelicula1", pelicula1.ToString() }, // Convertir a string
            { "pelicula2", pelicula2.ToString() }, // Convertir a string
            { "pelicula3", pelicula3.ToString() },
            { "pelicula4", pelicula4.ToString() },
            { "pelicula5", pelicula5.ToString() }  // Convertir a string
        };

        // Reemplazar el documento existente o insertar uno nuevo
        var result = collection.ReplaceOne(filter, document, new ReplaceOptions { IsUpsert = true });

        Console.WriteLine($"Datos guardados en MongoDB para el usuario: {usuario}");

        if (result.IsAcknowledged && result.ModifiedCount > 0)
        {
            Console.WriteLine($"Registro actualizado en MongoDB para el usuario: {usuario}");
        }
    }
}
