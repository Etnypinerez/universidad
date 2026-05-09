import json
import os
from datetime import datetime

class TDA_Log:
    """Clase maestra para el TDA de Auditoría (Logs)."""

    class NodoEvento:
        """
        Representa un evento de error o auditoría en el sistema.
        """
        def __init__(self, codigo_error, descripcion):
            self.fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.codigo_error = codigo_error
            self.descripcion = descripcion
            self.siguiente = None

        def a_diccionario(self):
            """Convierte el evento a diccionario para persistencia."""
            return {
                "fecha_hora": self.fecha_hora,
                "codigo_error": self.codigo_error,
                "descripcion": self.descripcion
            }

    class ListaLogs:
        """
        TDA que gestiona el registro de errores mediante una Lista Enlazada Simple.
        Incluye persistencia en archivos JSON.
        """
        def __init__(self, archivo_logs="registro_errores.json"):
            self.cabeza = None
            self.archivo_logs = archivo_logs
            self.total_eventos = 0
            # Cargamos logs previos
            self.cargar_desde_json()

        def registrar_error(self, codigo, descripcion):
            """
            Agrega un nuevo error al final de la lista de eventos.
            """
            nuevo_evento = TDA_Log.NodoEvento(codigo, descripcion)
            
            if self.cabeza is None:
                self.cabeza = nuevo_evento
            else:
                # Recorremos hasta el final para mantener orden cronológico
                actual = self.cabeza
                while actual.siguiente:
                    actual = actual.siguiente
                actual.siguiente = nuevo_evento
            
            self.total_eventos += 1
            self.guardar_en_json()
            print(f"[LOG REISTRADO] {codigo}: {descripcion}")

        def mostrar_logs(self):
            """Muestra todos los eventos registrados en consola."""
            if self.cabeza is None:
                print("No hay eventos registrados.")
                return

            print("\n--- REGISTRO DE AUDITORÍA ---")
            actual = self.cabeza
            while actual:
                print(f"{actual.fecha_hora} | Código: {actual.codigo_error} | {actual.descripcion}")
                actual = actual.siguiente

        def guardar_en_json(self):
            """Persiste los logs en formato JSON."""
            lista_datos = []
            actual = self.cabeza
            while actual:
                lista_datos.append(actual.a_diccionario())
                actual = actual.siguiente
            
            try:
                with open(self.archivo_logs, 'w', encoding='utf-8') as f:
                    json.dump(lista_datos, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"Error al guardar logs: {e}")

        def cargar_desde_json(self):
            """Recupera los logs desde el archivo JSON."""
            if not os.path.exists(self.archivo_logs):
                return

            try:
                with open(self.archivo_logs, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    for d in datos:
                        # Reconstruimos los nodos preservando la fecha original
                        nuevo = TDA_Log.NodoEvento(d['codigo_error'], d['descripcion'])
                        nuevo.fecha_hora = d['fecha_hora']
                        
                        if self.cabeza is None:
                            self.cabeza = nuevo
                        else:
                            # Buscamos el final para insertar
                            actual = self.cabeza
                            while actual.siguiente:
                                actual = actual.siguiente
                            actual.siguiente = nuevo
                        self.total_eventos += 1
            except Exception as e:
                print(f"Error al cargar logs: {e}")

# --- SECCIÓN DE PRUEBAS ---
if __name__ == "__main__":
    bitacora = TDA_Log.ListaLogs()
    
    # Simulación de errores
    if bitacora.total_eventos == 0:
        bitacora.registrar_error("AUTH_001", "Fallo de autenticación: API Key inválida.")
        bitacora.registrar_error("MEM_002", "Desbordamiento de cola: Ventana de contexto excedida.")
        bitacora.registrar_error("ID_003", "Búsqueda fallida: ID '9999' no encontrado.")
    
    bitacora.mostrar_logs()
