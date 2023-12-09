from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins='*')

# Obtener el número total de filas en el archivo CSV
total_filas = sum(1 for _ in open('data.csv'))

# Calcular el valor de skiprows para leer los últimos 10 millones de datos
skip_rows = max(0, total_filas - 20000000)

# Cargar los últimos 10 millones de datos desde el archivo CSV
data_parte_otra_instancia = pd.read_csv('data.csv', skiprows=range(1, skip_rows + 1), nrows=10000000)
segunda_fila = data_parte_otra_instancia.iloc[1:2]
print("Segunda fila:\n", segunda_fila)
# Imprimir la última fila
ultima_fila = data_parte_otra_instancia.iloc[-1:]
print("\nÚltima fila:\n", ultima_fila)

@app.route('/procesar', methods=['POST'])
def procesar():
    try:
        user_data = request.json
        print('Usuario recibido en la otra instancia:', user_data)

        # Eliminar la clave '_id' del usuario recibido
        user_data.pop('_id', None)

        # Convertir datos a arrays NumPy para cálculos más eficientes
        user_ratings = np.array([int(user_data[f'pelicula{i}']) for i in range(1, 6)])
        data_ratings = data_parte_otra_instancia.iloc[:, 1:6].values.astype(int)

        # Calcular la distancia euclidiana entre el usuario enviado y todos los usuarios en el conjunto de datos
        distancias = np.linalg.norm(data_ratings - user_ratings, axis=1)

        # Encontrar el índice del usuario con la distancia euclidiana más baja
        vecino_mas_cercano_index = np.argmin(distancias)

        vecino_mas_cercano_otra_instancia = data_parte_otra_instancia.iloc[vecino_mas_cercano_index].to_dict()

        # Incluir la distancia en la respuesta
        distancia_del_vecino_mas_cercano = distancias[vecino_mas_cercano_index]

        # Preparar la respuesta
        respuesta = {
            'vecino_mas_cercano': vecino_mas_cercano_otra_instancia,
            'distancia_del_vecino_mas_cercano': distancia_del_vecino_mas_cercano,
            'usuario_recibido': user_data['usuario'],
        }

        return jsonify(respuesta)

    except Exception as e:
        print('Error en la función procesar en la otra instancia:', str(e))
        return jsonify({'error': 'Error interno en la otra instancia'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Puerto diferente para la otra instancia
