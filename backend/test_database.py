from database import obtener_conexion

try:
    conexion = obtener_conexion()

    print("Conexion con PostgreSQL realizada correctamente.")

    conexion.close()

except Exception as error:
    print("Error al conectar con PostgreSQL:")
    print(error)
