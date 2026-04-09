import os
import requests
import json
import sys
import threading
import time

# --- CONFIGURACIÓN ---
# Coloca tu API Key de OpenRouter aquí
API_KEY = "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"
MODELO = "openrouter/auto"
# ---------------------

def animacion_carga(stop_event):
    """Muestra un spinner animado en la consola."""
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r\033[94m{chars[i % len(chars)]} Procesando...\033[0m")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * 25 + "\r")
    sys.stdout.flush()

def chat():
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Encabezado estilo Pro
    print("\033[95m" + "═"*55 + "\033[0m")
    print("       🚀 OPENROUTER CLI v4.0 (Multi-File)")
    print("  Comandos:")
    print("  .exit  -> Salir")
    print("  .clear -> Limpiar historial")
    print("  .file <archivo> <prompt> -> Leer 1 archivo")
    print("  .files <archivo1> <archivo2> -- <prompt> -> Leer Varios")
    print("\033[95m" + "═"*55 + "\033[0m")
    
    # Inicialización del historial
    messages = [{"role": "system", "content": "Eres un asistente de IA eficiente. Cuando se te proporcionen archivos, analízalos cuidadosamente según las instrucciones del usuario."}]

    while True:
        try:
            print("\033[92m\nTú:\033[0m")
            user_input = input(" ❯ ").strip()
            
            if not user_input:
                continue

            # --- GESTIÓN DE COMANDOS ---
            if user_input.lower() == ".exit":
                print("\n\033[91mTerminando proceso. ¡Hasta la próxima!\033[0m")
                break
                
            elif user_input.lower() == ".clear":
                messages = [{"role": "system", "content": "Eres un asistente de IA eficiente."}]
                print("\n\033[93m✨ Historial de mensajes vaciado con éxito.\033[0m")
                continue

            # Comando .file (Un solo archivo)
            elif user_input.lower().startswith(".file "):
                partes = user_input.split(maxsplit=2)
                if len(partes) < 2:
                    print("\033[91m❌ Uso incorrecto. Ejemplo: .file index.html explica este código\033[0m")
                    continue
                
                nombre_archivo = partes[1]
                instruccion = partes[2] if len(partes) > 2 else ""
                ruta_archivo = os.path.join(os.getcwd(), nombre_archivo)
                
                if not os.path.isfile(ruta_archivo):
                    print(f"\033[91m❌ Error: No se encontró '{nombre_archivo}' en la ruta actual.\033[0m")
                    continue
                
                try:
                    with open(ruta_archivo, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                    prompt_ensamblado = f"{nombre_archivo}:\n```\n{contenido}\n```\n{instruccion}"
                    messages.append({"role": "user", "content": prompt_ensamblado})
                    print(f"\033[93m[📂 '{nombre_archivo}' leído e inyectado con éxito]\033[0m")
                except UnicodeDecodeError:
                    print(f"\033[91m❌ Error: '{nombre_archivo}' no parece ser de texto válido.\033[0m")
                    continue
                except Exception as e:
                    print(f"\033[91m❌ Error inesperado: {e}\033[0m")
                    continue

            # Comando .files (Múltiples archivos con delimitador '--')
            elif user_input.lower().startswith(".files "):
                if "--" not in user_input:
                    print("\033[91m❌ Uso incorrecto. Falta el delimitador '--'. Ejemplo: .files app.py utils.py -- revisa esto\033[0m")
                    continue

                # Dividir en dos grandes bloques
                bloque_archivos, instruccion = user_input.split("--", 1)
                instruccion = instruccion.strip()

                # Limpiar la palabra comando y obtener lista de nombres
                nombres_archivos = bloque_archivos[7:].strip().split()

                if not nombres_archivos:
                    print("\033[91m❌ Error: No escribiste nombres de archivos antes del '--'.\033[0m")
                    continue

                # 1. Validación: Comprobar que TODOS existan antes de leer nada
                todos_existen = True
                rutas_validas = []
                for nombre in nombres_archivos:
                    ruta = os.path.join(os.getcwd(), nombre)
                    if not os.path.isfile(ruta):
                        print(f"\033[91m❌ Error: No se encontró el archivo '{nombre}'. Petición cancelada.\033[0m")
                        todos_existen = False
                        break # Cortamos si falta uno
                    rutas_validas.append((nombre, ruta))

                if not todos_existen:
                    continue # Volvemos a pedir input si hubo error

                # 2. Lectura y Ensamblado del Super-Prompt
                hubo_error_lectura = False
                bloque_contexto = f"Archivos cargados para análisis:\n"
                
                for nombre, ruta in rutas_validas:
                    try:
                        with open(ruta, 'r', encoding='utf-8') as f:
                            contenido = f.read()
                        bloque_contexto += f"\n--- {nombre} ---\n```\n{contenido}\n```\n"
                    except UnicodeDecodeError:
                        print(f"\033[91m❌ Error: '{nombre}' es binario o tiene formato incorrecto. Petición cancelada.\033[0m")
                        hubo_error_lectura = True
                        break
                    except Exception as e:
                        print(f"\033[91m❌ Error inesperado al leer '{nombre}': {e}\033[0m")
                        hubo_error_lectura = True
                        break

                if hubo_error_lectura:
                    continue

                # Unir los archivos con la instrucción del usuario
                prompt_ensamblado = f"{bloque_contexto}\n---\n**Instrucción:** {instruccion}"
                
                # Enviar a la memoria de la IA
                messages.append({"role": "user", "content": prompt_ensamblado})
                print(f"\033[93m[📂 {len(nombres_archivos)} archivos leídos e inyectados al contexto]\033[0m")

            else:
                # Flujo normal de chat
                messages.append({"role": "user", "content": user_input})
            # ---------------------------

            # Iniciar hilo de animación
            stop_event = threading.Event()
            spinner_thread = threading.Thread(target=animacion_carga, args=(stop_event,))
            spinner_thread.start()

            payload = {
                "model": MODELO,
                "messages": messages,
                "stream": True
            }
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-OpenRouter-Title": "Pydroid CLI v4"
            }

            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload), stream=True)
                
                # Detener spinner
                stop_event.set()
                spinner_thread.join()

                if response.status_code == 200:
                    print("\033[96mIA:\033[0m")
                    full_response = ""
                    
                    for line in response.iter_lines():
                        if line:
                            str_line = line.decode('utf-8').replace('data: ', '')
                            if str_line == '[DONE]': break
                            try:
                                j_line = json.loads(str_line)
                                content = j_line['choices'][0]['delta'].get('content', '')
                                print(content, end="", flush=True)
                                full_response += content
                            except: continue
                    
                    print("\n" + "\033[90m" + "─" * 30 + "\033[0m")
                    messages.append({"role": "assistant", "content": full_response})
                else:
                    print(f"\n\033[91m❌ Error de API: {response.status_code}\033[0m")
                    print(f"Detalle: {response.text}")

            except requests.exceptions.RequestException as e:
                stop_event.set()
                print(f"\n\033[91m❌ Error de conexión: {e}\033[0m")

        except KeyboardInterrupt:
            print("\n\nSaliendo...")
            break
        except Exception as e:
            print(f"\n\033[91m❌ Error inesperado: {e}\033[0m")

if __name__ == "__main__":
    import os
    chat()
