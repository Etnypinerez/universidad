import json
import os

class TDA_Contexto:
    """Clase maestra para el TDA de Contexto de Conversación."""

    class NodoMensaje:
        """
        Representa un nodo individual en la cola de mensajes.
        Contiene el rol (usuario o modelo) y el contenido del mensaje.
        """
        def __init__(self, rol, contenido):
            self.rol = rol  # 'user' o 'model'
            self.contenido = contenido
            self.siguiente = None

        def a_diccionario(self):
            """Convierte el mensaje a diccionario para JSON."""
            return {"rol": self.rol, "contenido": self.contenido}

    class ColaConversacion:
        """
        TDA que gestiona el contexto de la conversación mediante una Cola.
        Implementa una ventana de contexto de tamaño fijo (N mensajes).
        """
        def __init__(self, limite=10):
            self.frente = None
            self.final = None
            self.limite = limite
            self.tamano_actual = 0

        def esta_vacia(self):
            """Verifica si la cola no tiene mensajes."""
            return self.frente is None

        def encolar(self, rol, contenido):
            """
            Agrega un nuevo mensaje al final de la cola.
            Si se excede el límite configurado, elimina el mensaje más antiguo (frente).
            """
            # Validación de datos
            if not rol or not contenido:
                return False, "Error: El rol y el contenido son obligatorios."

            # Si llegamos al límite, quitamos el más viejo
            if self.tamano_actual >= self.limite:
                self.desencolar()

            nuevo_nodo = TDA_Contexto.NodoMensaje(rol, contenido)
            if self.esta_vacia():
                self.frente = nuevo_nodo
                self.final = nuevo_nodo
            else:
                self.final.siguiente = nuevo_nodo
                self.final = nuevo_nodo
            
            self.tamano_actual += 1
            return True, "Mensaje agregado al contexto."

        def desencolar(self):
            """Elimina el mensaje más antiguo de la cola (el frente)."""
            if self.esta_vacia():
                return None
            
            nodo_eliminado = self.frente
            self.frente = self.frente.siguiente
            
            if self.frente is None:
                self.final = None
                
            self.tamano_actual -= 1
            return nodo_eliminado

        def obtener_mensajes_lista(self):
            """Retorna una lista de diccionarios con el historial actual."""
            mensajes = []
            actual = self.frente
            while actual:
                mensajes.append(actual.a_diccionario())
                actual = actual.siguiente
            return mensajes

        def guardar_json(self, bot_id):
            """
            Guarda el historial de la cola en un archivo JSON específico para el bot.
            Se usa el ID del bot para nombrar el archivo.
            """
            nombre_archivo = f"historial_bot_{bot_id}.json"
            datos = self.obtener_mensajes_lista()
            
            try:
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    json.dump(datos, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"Error al guardar historial del bot {bot_id}: {e}")

        def cargar_json(self, bot_id):
            """
            Carga el historial de mensajes desde el archivo JSON del bot.
            Reconstruye la cola respetando el límite de mensajes.
            """
            nombre_archivo = f"historial_bot_{bot_id}.json"
            if not os.path.exists(nombre_archivo):
                return

            try:
                with open(nombre_archivo, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    # Limpiamos cola actual antes de cargar
                    self.frente = None
                    self.final = None
                    self.tamano_actual = 0
                    
                    for msg in datos:
                        self.encolar(msg['rol'], msg['contenido'])
            except Exception as e:
                print(f"Error al cargar historial del bot {bot_id}: {e}")

# --- SECCIÓN DE PRUEBAS Y DATOS POR DEFECTO ---

def probar_cola():
    """Función para demostrar el funcionamiento del módulo de contexto."""
    cola = TDA_Contexto.ColaConversacion(limite=3) # Límite pequeño para probar ventana
    print("--- Probando ventana de contexto (Límite: 3) ---")
    
    cola.encolar("user", "Hola, ¿quién eres?")
    cola.encolar("model", "Soy un asistente virtual.")
    cola.encolar("user", "¿Cómo estás?")
    
    print("Contenido antes de exceder el límite:")
    for m in cola.obtener_mensajes_lista():
        print(f"[{m['rol']}]: {m['contenido']}")
        
    print("\nAgregando cuarto mensaje (debería eliminar el primero)...")
    cola.encolar("model", "¡Bien! ¿Y tú?")
    
    print("\nContenido después de exceder el límite:")
    for m in cola.obtener_mensajes_lista():
        print(f"[{m['rol']}]: {m['contenido']}")
    
    # Prueba de guardado
    cola.guardar_json("test_bot")
    print("\nHistorial guardado en 'historial_bot_test_bot.json'.")

if __name__ == "__main__":
    probar_cola()
