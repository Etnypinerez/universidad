import json

class TDA_Restauracion:
    """Clase maestra para el TDA de Restauración (Pila)."""

    class NodoEstado:
        """
        Representa un estado previo del bot en la Pila.
        Almacena los valores que pueden cambiar y ser restaurados.
        """
        def __init__(self, instruccion, temperatura):
            self.instruccion = instruccion
            self.temperatura = temperatura
            self.siguiente = None  # Puntero al elemento inferior en la pila

        def a_diccionario(self):
            return {
                "instruccion": self.instruccion,
                "temperatura": self.temperatura
            }

    class PilaRestauracion:
        """
        TDA Pila (LIFO) para gestionar el historial de cambios de configuración.
        """
        def __init__(self):
            self.cima = None
            self.total_estados = 0

        def esta_vacia(self):
            return self.cima is None

        def apilar(self, instruccion, temperatura):
            """Guarda un nuevo estado en la cima de la pila."""
            # Validación de datos
            if instruccion is None or temperatura is None:
                return False
                
            nuevo_nodo = TDA_Restauracion.NodoEstado(instruccion, temperatura)
            nuevo_nodo.siguiente = self.cima
            self.cima = nuevo_nodo
            self.total_estados += 1
            return True

        def desapilar(self):
            """Retorna y elimina el último estado guardado."""
            if self.esta_vacia():
                return None
            
            estado = self.cima
            self.cima = self.cima.siguiente
            self.total_estados -= 1
            return estado

        def a_lista(self):
            """Convierte la pila a una lista para persistencia JSON."""
            lista = []
            actual = self.cima
            while actual:
                lista.append(actual.a_diccionario())
                actual = actual.siguiente
            return lista

        def cargar_desde_lista(self, datos_lista):
            """Reconstruye la pila a partir de una lista guardada (manteniendo el orden)."""
            # Como la lista viene en orden Cima -> Fondo, la recorremos al revés
            # para que al apilar quede en el orden correcto.
            for item in reversed(datos_lista):
                self.apilar(item['instruccion'], item['temperatura'])

# --- PRUEBA DEL MÓDULO ---
if __name__ == "__main__":
    pila = TDA_Restauracion.PilaRestauracion()
    print("Apilando estados...")
    pila.apilar("Eres un pirata", 0.7)
    pila.apilar("Eres un robot", 0.1)
    
    print(f"Cima actual: {pila.cima.instruccion} (Temp: {pila.cima.temperatura})")
    
    ultimo = pila.desapilar()
    print(f"Estado restaurado: {ultimo.instruccion}")
    print(f"Nueva cima: {pila.cima.instruccion}")
