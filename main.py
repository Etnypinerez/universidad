import os
import sys
from modulos.persistencia import TDA_Persistencia
from modulos.log import TDA_Log

class SistemaChatbot:
    """
    Clase Maestra que engloba toda la lógica de la aplicación 'Chatbot'.
    Contiene sub-clases internas para organizar las responsabilidades.
    """

    class InterfazVisual:
        """Clase interna para manejo de estética y terminal."""
        VERDE = "\033[92m"
        AZUL = "\033[94m"
        ROJO = "\033[91m"
        AMARILLO = "\033[93m"
        RESET = "\033[0m"

        @staticmethod
        def limpiar():
            os.system('cls' if os.name == 'nt' else 'clear')

        @classmethod
        def mostrar_titulo(cls, texto):
            print(f"\n{cls.AZUL}{'='*60}")
            print(f" {texto.center(58)}")
            print(f"{'='*60}{cls.RESET}")

    class ValidadorEntradas:
        """Clase interna para validación de datos del usuario."""
        @staticmethod
        def entero(mensaje, bitacora):
            while True:
                try:
                    return int(input(mensaje))
                except ValueError:
                    print(f"\033[91mError: Ingrese un número válido.\033[0m")
                    bitacora.registrar_error("VAL_INT_ERR", "Entrada no numérica en menú.")

        @staticmethod
        def decimal(mensaje, bitacora):
            while True:
                try:
                    entrada = input(mensaje)
                    if not entrada: return None
                    return float(entrada)
                except ValueError:
                    print(f"\033[91mError: Debe ser un número decimal.\033[0m")
                    bitacora.registrar_error("VAL_FLOAT_ERR", "Entrada decimal inválida.")

    class GestorPerfiles:
        """Clase interna para operaciones de configuración (Módulo 1)."""
        def __init__(self, sistema):
            self.sistema = sistema

        def ejecutar_menu(self):
            while True:
                self.sistema.InterfazVisual.mostrar_titulo("CONFIGURACIÓN DE CHATBOT")
                print("1. Listar bots registrados")
                print("2. Registrar nuevo bot")
                print("3. Modificar bot (con Pila de Restauración)")
                print("4. Eliminar bot")
                print("5. Volver al menú principal")
                
                op = self.sistema.ValidadorEntradas.entero("\nSeleccione: ", self.sistema.bitacora)
                if op == 1: self.listar()
                elif op == 2: self.crear()
                elif op == 3: self.modificar()
                elif op == 4: self.eliminar()
                elif op == 5: break

        def listar(self):
            self.sistema.InterfazVisual.mostrar_titulo("LISTADO DE BOTS")
            actual = self.sistema.configuracion.primero
            if not actual:
                print("No hay bots configurados.")
            while actual:
                print(f"ID: {actual.id_unico} | Nombre: {actual.nombre} | Instrucción: {actual.instruccion_sistema[:30]}...")
                actual = actual.siguiente
            input("\nPresione Enter...")

        def crear(self):
            print("\n-- NUEVO PERFIL --")
            print(f"{self.sistema.InterfazVisual.AMARILLO}Tip: Consigue tu API Key en https://aistudio.google.com/app/apikey{self.sistema.InterfazVisual.RESET}")
            id_u = input("ID Único: ")
            nom = input("Nombre: ")
            mod = input("Modelo (gemini-1.5-flash / gemini-1.5-pro): ")
            key = input("API Key: ")
            ins = input("Instrucciones de sistema: ")
            exito, msj = self.sistema.configuracion.agregar_bot(id_u, nom, mod, key, ins)
            print(msj)

        def modificar(self):
            id_u = input("ID del bot: ")
            bot = self.sistema.configuracion.buscar_bot(id_u)
            if bot:
                bot.guardar_estado_previo() # Módulo 3 (Pila)
                print(f"Modificando bot: {bot.nombre}")
                print(f"{self.sistema.InterfazVisual.AMARILLO}Tip: Obtén una nueva key en https://aistudio.google.com/app/apikey{self.sistema.InterfazVisual.RESET}")
                bot.nombre = input(f"Nuevo nombre [{bot.nombre}]: ") or bot.nombre
                bot.modelo = input(f"Nuevo modelo [{bot.modelo}]: ") or bot.modelo
                bot.instruccion_sistema = input("Nuevas instrucciones: ") or bot.instruccion_sistema
                temp = self.sistema.ValidadorEntradas.decimal(f"Nueva temperatura [{bot.temperatura}]: ", self.sistema.bitacora)
                if temp is not None: bot.temperatura = temp
                print("Bot actualizado.")
            else:
                print("Bot no encontrado.")

        def eliminar(self):
            id_u = input("ID a eliminar: ")
            if self.sistema.configuracion.eliminar_bot(id_u):
                print("Bot eliminado.")
            else:
                print("No se pudo eliminar.")

    class GestorChat:
        """Clase interna para interacciones (Módulo 2)."""
        def __init__(self, sistema):
            self.sistema = sistema

        def iniciar_conversacion(self):
            id_u = input("ID del bot: ")
            bot = self.sistema.configuracion.buscar_bot(id_u)
            if not bot:
                print("Bot no encontrado.")
                return

            # Intentar configurar la IA de Google
            genai_disponible = False
            try:
                import google.generativeai as genai
                genai.configure(api_key=bot.obtener_api_key())
                
                # Intentar determinar el mejor modelo disponible
                target_model = bot.modelo.lower()
                # Lista de prioridades para fallback
                api_model = "gemini-1.5-flash" 
                
                try:
                    models = genai.list_models()
                    available_names = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
                    
                    # 1. Buscar coincidencia exacta
                    exact_match = [m for m in available_names if target_model == m.lower() or f"models/{target_model}" == m.lower()]
                    if exact_match:
                        api_model = exact_match[0]
                    else:
                        # 2. Buscar coincidencia parcial
                        potential = [m for m in available_names if target_model in m.lower()]
                        if potential:
                            api_model = potential[0]
                        else:
                            # 3. Buscar cualquier flash si no hay coincidencia
                            flash_models = [m for m in available_names if "flash" in m.lower()]
                            if flash_models:
                                api_model = flash_models[0]
                            elif available_names:
                                api_model = available_names[0]
                except Exception:
                    # Si falla el listing, usamos un nombre que suele funcionar en v1
                    if "pro" in target_model: api_model = "gemini-1.5-pro"
                    else: api_model = "gemini-1.5-flash"

                model = genai.GenerativeModel(
                    model_name=api_model,
                    system_instruction=bot.instruccion_sistema
                )
                genai_disponible = True
            except ImportError:
                print(f"{self.sistema.InterfazVisual.AMARILLO}Aviso: Librería 'google-generativeai' no instalada. Usando modo simulación.{self.sistema.InterfazVisual.RESET}")
            except Exception as e:
                print(f"{self.sistema.InterfazVisual.ROJO}Error configurando API: {e}{self.sistema.InterfazVisual.RESET}")
                self.sistema.bitacora.registrar_error("API_CONFIG_ERR", str(e))

            while True:
                self.sistema.InterfazVisual.mostrar_titulo(f"SALA DE CHAT: {bot.nombre}")
                print("1. Enviar mensaje")
                print("2. Ver historial (Cola)")
                print("3. Restaurar estado anterior (Pila)")
                print("4. Salir")
                
                op = self.sistema.ValidadorEntradas.entero("\nAcción: ", self.sistema.bitacora)
                if op == 1:
                    txt = input("Tú: ")
                    bot.cola_mensajes.encolar("user", txt)
                    
                    if genai_disponible:
                        try:
                            print(f"{self.sistema.InterfazVisual.AMARILLO}Escribiendo...{self.sistema.InterfazVisual.RESET}")
                            
                            # Convertimos el historial de la cola al formato de Gemini
                            historial = []
                            mensajes_lista = bot.cola_mensajes.obtener_mensajes_lista()
                            
                            # Solo los mensajes anteriores al actual
                            for m in mensajes_lista[:-1]:
                                role = "user" if m['rol'] == "user" else "model"
                                historial.append({"role": role, "parts": [m['contenido']]})
                            
                            # Iniciamos chat con el historial corregido
                            chat = model.start_chat(history=historial)
                            response = chat.send_message(
                                txt, 
                                generation_config={
                                    "temperature": bot.temperatura,
                                    "top_p": 0.95,
                                    "top_k": 40,
                                    "max_output_tokens": 2048,
                                }
                            )
                            resp = response.text
                        except Exception as e:
                            resp = f"[Error de API: {e}]"
                            print(f"{self.sistema.InterfazVisual.ROJO}Error en respuesta: {e}{self.sistema.InterfazVisual.RESET}")
                            self.sistema.bitacora.registrar_error("API_RESP_ERR", str(e))
                    else:
                        resp = f"[Modo Simulación] Hola, soy {bot.nombre}. No puedo contactar a Gemini sin la librería instalada."

                    print(f"\n{self.sistema.InterfazVisual.VERDE}{bot.nombre}: {resp}{self.sistema.InterfazVisual.RESET}")
                    bot.cola_mensajes.encolar("model", resp)
                elif op == 2:
                    for m in bot.cola_mensajes.obtener_mensajes_lista():
                        print(f"[{m['rol'].upper()}]: {m['contenido']}")
                    input("\nEnter...")
                elif op == 3:
                    if bot.restaurar_estado(): print("Estado restaurado.")
                    else: print("No hay estados previos.")
                elif op == 4: break

    def __init__(self):
        """Inicializa el Sistema Chatbot y sus componentes."""
        self.bitacora = TDA_Log.ListaLogs()
        self.motor = TDA_Persistencia.MotorPersistencia()
        self.configuracion, msj = self.motor.cargar_todo()
        
        # Instanciamos los gestores internos
        self.gestor_perfiles = self.GestorPerfiles(self)
        self.gestor_chat = self.GestorChat(self)
        
        print(f"[SISTEMA] {msj}")

    def menu_principal(self):
        """Bucle principal del programa."""
        while True:
            self.InterfazVisual.mostrar_titulo("PROYECTO: CHATBOT")
            print(f"1. Gestionar Perfiles ({self.configuracion.cantidad_nodos} bots)")
            print("2. Abrir Sala de Chat")
            print("3. Consultar Logs de Error")
            print("4. Guardar y Salir")
            
            opcion = self.ValidadorEntradas.entero("\nOpcion: ", self.bitacora)

            if opcion == 1: self.gestor_perfiles.ejecutar_menu()
            elif opcion == 2: self.gestor_chat.iniciar_conversacion()
            elif opcion == 3: self.bitacora.mostrar_logs(); input("\nEnter...")
            elif opcion == 4:
                self.motor.guardar_todo(self.configuracion)
                print("Persistencia finalizada. Cerrando Chatbot...")
                break
            else:
                print("Opción inválida.")

if __name__ == "__main__":
    # Ejecución del sistema Chatbot
    app = SistemaChatbot()
    app.menu_principal()
