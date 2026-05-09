import json
import os
import base64

from .contexto import TDA_Contexto
from .restauracion import TDA_Restauracion

class TDA_Configuracion:
    """Clase maestra que engloba el TDA de Configuración de Chatbots."""
    
    class NodoBot:
        """
        Representa un nodo en la Lista Doblemente Enlazada.
        Incluye punteros a la Pila de Restauración y Cola de Mensajes.
        """
        def __init__(self, id_unico, nombre, modelo, api_key, instruccion_sistema, temperatura=1.0):
            self.id_unico = str(id_unico)
            self.nombre = nombre
            self.modelo = modelo
            self.api_key_protegida = base64.b64encode(api_key.encode()).decode()
            self.instruccion_sistema = instruccion_sistema
            self.temperatura = temperatura 
            
            # Estructuras Hijas (Módulos 2 y 3)
            self.pila_restauracion = TDA_Restauracion.PilaRestauracion()
            self.cola_mensajes = TDA_Contexto.ColaConversacion(limite=10)
            
            # Punteros Lista Doblemente Enlazada
            self.siguiente = None
            self.anterior = None

        def obtener_api_key(self):
            return base64.b64decode(self.api_key_protegida.encode()).decode()

        def guardar_estado_previo(self):
            """Antes de modificar, guarda el estado actual en la pila."""
            self.pila_restauracion.apilar(self.instruccion_sistema, self.temperatura)

        def restaurar_estado(self):
            """Saca el último estado de la pila y lo aplica."""
            estado = self.pila_restauracion.desapilar()
            if estado:
                self.instruccion_sistema = estado.instruccion
                self.temperatura = estado.temperatura
                return True
            return False

        def a_diccionario(self):
            return {
                "id_unico": self.id_unico,
                "nombre": self.nombre,
                "modelo": self.modelo,
                "api_key_protegida": self.api_key_protegida,
                "instruccion_sistema": self.instruccion_sistema,
                "temperatura": self.temperatura,
                "historial_mensajes": self.cola_mensajes.obtener_mensajes_lista(),
                "historial_estados": self.pila_restauracion.a_lista()
            }

    class ListaConfiguracion:
        """Estructura de Lista Doblemente Enlazada para gestionar los bots."""
        def __init__(self):
            self.primero = None
            self.ultimo = None
            self.cantidad_nodos = 0

        def agregar_bot(self, id_unico, nombre, modelo, api_key, instruccion_sistema, temperatura=1.0):
            if self.buscar_bot(id_unico):
                return False, f"Error: ID {id_unico} ya existe."

            # Acceso a NodoBot como clase interna
            nuevo_nodo = TDA_Configuracion.NodoBot(id_unico, nombre, modelo, api_key, instruccion_sistema, temperatura)
            
            if self.primero is None:
                self.primero = nuevo_nodo
                self.ultimo = nuevo_nodo
            else:
                self.ultimo.siguiente = nuevo_nodo
                nuevo_nodo.anterior = self.ultimo
                self.ultimo = nuevo_nodo
            
            self.cantidad_nodos += 1
            return True, "Bot registrado."

        def buscar_bot(self, id_unico):
            actual = self.primero
            id_str = str(id_unico)
            while actual:
                if actual.id_unico == id_str:
                    return actual
                actual = actual.siguiente
            return None

        def eliminar_bot(self, id_unico):
            bot = self.buscar_bot(id_unico)
            if not bot: return False
            if bot.anterior: bot.anterior.siguiente = bot.siguiente
            else: self.primero = bot.siguiente
            if bot.siguiente: bot.siguiente.anterior = bot.anterior
            else: self.ultimo = bot.anterior
            self.cantidad_nodos -= 1
            return True

        def listar_todos(self):
            """Muestra en consola todos los perfiles cargados."""
            actual = self.primero
            if not actual:
                print("La lista está vacía.")
                return
            
            while actual:
                print(f"[{actual.id_unico}] {actual.nombre} - Modelo: {actual.modelo}")
                actual = actual.siguiente

# --- SECCIÓN DE PRUEBAS Y DATOS POR DEFECTO ---

def cargar_datos_prueba(tda_config):
    """Carga ejemplos por defecto si la lista está vacía."""
    if tda_config.cantidad_nodos == 0:
        tda_config.agregar_bot(
            "1001", "Asistente Creativo", "Modelo-Estandar", 
            "CLAVE_EJEMPLO_1", "Eres un experto en literatura y redacción creativa."
        )
        tda_config.agregar_bot(
            "1002", "Analista de Datos", "Modelo-Avanzado", 
            "CLAVE_EJEMPLO_2", "Eres un científico de datos experto en Python y SQL."
        )
        print("Datos de prueba cargados exitosamente.")

if __name__ == "__main__":
    # Ajuste para permitir ejecución directa de pruebas
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    
    config = TDA_Configuracion.ListaConfiguracion()
    cargar_datos_prueba(config)
    print("\n--- Lista de Bots Actuales ---")
    config.listar_todos()
