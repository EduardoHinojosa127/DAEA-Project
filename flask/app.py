from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, origins='*')

# Cargar datos desde el archivo CSV
data = pd.read_csv('data.csv', nrows=10000000)

# Lista de URLs de instancias adicionales
instancias = ["http://54.161.217.131:5000/procesar", "http://34.200.70.170:5000/procesar", "http://44.216.219.218:5000/procesar", "http://3.215.220.204:5000/procesar"]

@app.route('/procesar', methods=['POST'])
def procesar():
    try:
        user_data = request.json
        app.logger.info('Usuario recibido: %s', user_data)

        # Eliminar la clave '_id' del usuario recibido
        user_data.pop('_id', None)

        # Convertir datos a arrays NumPy para cálculos más eficientes
        user_ratings = np.array([int(user_data[f'pelicula{i}']) for i in range(1, 6)])
        data_ratings = data.iloc[:, 1:6].values.astype(int)

        # Calcular la distancia euclidiana entre el usuario enviado y todos los usuarios en el conjunto de datos
        distancias = np.linalg.norm(data_ratings - user_ratings, axis=1)

        # Encontrar el índice del usuario con la distancia euclidiana más baja
        vecino_mas_cercano_index = np.argmin(distancias)

        vecino_mas_cercano = data.iloc[vecino_mas_cercano_index].to_dict()

        # Imprimir la distancia calculada por la instancia actual
        app.logger.info('Distancia calculada por la instancia actual: %s', distancias[vecino_mas_cercano_index])

        # Lógica para comparar distancias con las otras instancias
        for instancia_url in instancias:
            otra_instancia_response = requests.post(instancia_url, json=user_data)
            otra_instancia_data = otra_instancia_response.json()
            vecino_mas_cercano_otra_instancia = otra_instancia_data.get('vecino_mas_cercano', {})
            distancia_vecino_otra_instancia = otra_instancia_data.get('distancia_del_vecino_mas_cercano')

            # Imprimir información de la otra instancia
            app.logger.info('Vecino mas cercano de la instancia en %s: %s', instancia_url, vecino_mas_cercano_otra_instancia)
            app.logger.info('Distancia al vecino más cercano de la instancia en %s: %s', instancia_url, distancia_vecino_otra_instancia)

            # Comparar distancias y asignar el nuevo vecino y la nueva distancia
            if distancia_vecino_otra_instancia < distancias[vecino_mas_cercano_index]:
                vecino_mas_cercano = vecino_mas_cercano_otra_instancia
                distancias[vecino_mas_cercano_index] = distancia_vecino_otra_instancia

        # Obtener la película recomendada del vecino más cercano
        pelicula_recomendada = obtener_pelicula_recomendada(vecino_mas_cercano)

        # Preparar la respuesta
        respuesta = {
            'vecino_mas_cercano': vecino_mas_cercano,
            'pelicula_recomendada': pelicula_recomendada,
            'usuario_recibido': user_data['usuario'],
        }

        return jsonify(respuesta)

    except Exception as e:
        app.logger.error('Error en la función procesar: %s', str(e))
        return jsonify({'error': 'Error interno'}), 500

def obtener_pelicula_recomendada(vecino):
    # Lógica para obtener la película recomendada del vecino más cercano
    # En este caso, se elige la película con la calificación más alta entre las películas 6 a 10

    # Crear una lista de tuplas (pelicula, calificacion) para las películas 6 a 10
    peliculas_calificaciones = [(f'pelicula{i}', vecino[f'pelicula{i}']) for i in range(6, 11)]

    # Encontrar la película con la calificación más alta
    pelicula_recomendada, _ = max(peliculas_calificaciones, key=lambda x: x[1])

    return pelicula_recomendada

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
