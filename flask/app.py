from flask import Flask, request, jsonify
import pandas as pd
import numpy as np  # Importa NumPy
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins='*')

# Cargar datos desde el archivo CSV
data = pd.read_csv('data.csv')

@app.route('/procesar', methods=['POST'])
def procesar():
    try:
        user_data = request.json
        print('Usuario recibido:', user_data)

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

        # Obtener la película recomendada del vecino más cercano
        pelicula_recomendada = obtener_pelicula_recomendada(vecino_mas_cercano)

        # Preparar la respuesta
        respuesta = {
            'vecino_mas_cercano': vecino_mas_cercano,
            'pelicula_recomendada': pelicula_recomendada
        }

        return jsonify(respuesta)
        
    except Exception as e:
        print('Error en la función procesar:', str(e))
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
    app.run(debug=True)
