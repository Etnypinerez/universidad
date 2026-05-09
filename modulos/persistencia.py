import json
import os
from .configuracion import TDA_Configuracion

class TDA_Persistencia:
    """Clase maestra para el TDA de Persistencia."""

    class MotorPersistencia:
        """
        TDA encargado de la serialización y reconstrucción de todas las estructuras (Módulo 4).
        """
        def __init__(self, archivo_ajustes="ajustes.json"):
            self.archivo_ajustes = archivo_ajustes
            self.ruta_db = self._cargar_ruta_db()

        def _cargar_ruta_db(self):
            """Lee la ruta del archivo JSON desde los ajustes."""
            if os.path.exists(self.archivo_ajustes):
                try:
                    with open(self.archivo_ajustes, 'r') as f:
                        config = json.load(f)
                        return config.get("ruta_base_datos", "base_datos_default.json")
                except:
                    return "base_datos_default.json"
            return "base_datos_default.json"

        def guardar_todo(self, lista_config):
            """
            Guarda la lista completa, incluyendo colas y pilas de cada bot.
            """
            datos_globales = []
            actual = lista_config.primero
            while actual:
                datos_globales.append(actual.a_diccionario())
                actual = actual.siguiente
            
            try:
                with open(self.ruta_db, 'w', encoding='utf-8') as f:
                    json.dump(datos_globales, f, indent=4, ensure_ascii=False)
                return True, f"Datos guardados en {self.ruta_db}"
            except Exception as e:
                return False, f"Error al guardar: {e}"

        def cargar_todo(self):
            """
            Reconstruye la red completa de chatbots.
            Restaura punteros de la lista, colas y pilas en el orden correcto.
            """
            nueva_lista = TDA_Configuracion.ListaConfiguracion()
            
            if not os.path.exists(self.ruta_db):
                return nueva_lista, "Archivo de base de datos no encontrado, se creó una lista vacía."

            try:
                with open(self.ruta_db, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    for d in datos:
                        # 1. Reconstruir Nodo de la Lista (Módulo 1)
                        bot = TDA_Configuracion.NodoBot(
                            id_unico=d['id_unico'],
                            nombre=d['nombre'],
                            modelo=d['modelo'],
                            api_key="", # La key ya viene codificada en d['api_key_protegida']
                            instruccion_sistema=d['instruccion_sistema'],
                            temperatura=d.get('temperatura', 1.0)
                        )
                        bot.api_key_protegida = d['api_key_protegida']
                        
                        # 2. Reconstruir Cola de Mensajes (Módulo 2)
                        for msg in d.get('historial_mensajes', []):
                            bot.cola_mensajes.encolar(msg['rol'], msg['contenido'])
                        
                        # 3. Reconstruir Pila de Estados (Módulo 3)
                        # Cargamos la lista de estados en la pila
                        bot.pila_restauracion.cargar_desde_lista(d.get('historial_estados', []))
                        
                        # 4. Insertar en la Lista Doblemente Enlazada
                        if nueva_lista.primero is None:
                            nueva_lista.primero = bot
                            nueva_lista.ultimo = bot
                        else:
                            nueva_lista.ultimo.siguiente = bot
                            bot.anterior = nueva_lista.ultimo
                            nueva_lista.ultimo = bot
                        nueva_lista.cantidad_nodos += 1
                        
                return nueva_lista, "Sistema reconstruido exitosamente."
            except Exception as e:
                return nueva_lista, f"Error en la reconstrucción: {e}"

# --- PRUEBA DEL MÓDULO 4 ---
if __name__ == "__main__":
    motor = TDA_Persistencia.MotorPersistencia()
    
    # Crear una lista de prueba
    lista = TDA_Configuracion.ListaConfiguracion()
    lista.agregar_bot("1", "Bot Test", "flash", "KEY123", "Instr 1")
    
    # Simular cambios y mensajes
    bot = lista.primero
    bot.cola_mensajes.encolar("user", "Hola motor")
    bot.guardar_estado_previo() # Guardar estado en Pila
    bot.instruccion_sistema = "Nueva instruccion"
    
    # Guardar todo
    motor.guardar_todo(lista)
    print("Estado guardado.")
    
    # Cargar en una nueva instancia
    lista_recuperada, msj = motor.cargar_todo()
    print(msj)
    bot_recup = lista_recuperada.buscar_bot("1")
    if bot_recup:
        print(f"Bot: {bot_recup.nombre}")
        print(f"Instrucción actual: {bot_recup.instruccion_sistema}")
        print(f"Mensajes en cola: {len(bot_recup.cola_mensajes.obtener_mensajes_lista())}")
        print(f"Estados en pila: {bot_recup.pila_restauracion.total_estados}")
