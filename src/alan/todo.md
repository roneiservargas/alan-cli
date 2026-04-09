# 📝 TODO: Implementación de Comando `.model`

### 1. Refactorización de la Clase `Config`
* **[ ] Cambiar `MODELO` estático por dinámico:** Eliminar la constante `MODELO = "openrouter/auto"` y convertirla en un método de clase `get_model()`.
* **[ ] Implementar `get_model()`:** * Buscar `ALAN_MODEL` en variables de entorno.
    * Si no existe, buscar la entrada `MODEL=` en `~/.alanrc`.
    * **Fallback:** Si nada está definido, retornar `"openrouter/auto"` por defecto.
* **[ ] Crear `set_model(model_name)`:** * Lógica para leer el contenido actual de `~/.alanrc`.
    * Si existe la línea `MODEL=`, actualizarla. 
    * Si no existe, apéndice `MODEL=model_name` al final del archivo.

### 2. Actualización de `AIClient`
* **[ ] Payload Dinámico:** Asegurar que el método `stream_chat` llame a `Config.get_model()` justo antes de enviar la petición, en lugar de usar un valor cargado al inicio. Esto permite cambiar el modelo en caliente durante la misma sesión.

### 3. Modificaciones en `ChatInterface`
* **[ ] Actualizar Lexer y Completer:** Añadir `.model` a la lista de palabras reservadas en `AlanLexer` y al diccionario del `completer`.
* **[ ] Crear método `handle_model()`:**
    * Lanzar un `prompt()` secundario (no multilínea) preguntando: *"Ingresa el código del modelo (ej: anthropic/claude-3-opus):"*.
    * Llamar a `Config.set_model()` con la entrada del usuario.
    * Mostrar un panel de confirmación verde notificando el cambio persistente.

### 4. Experiencia de Usuario (UI)
* **[ ] Actualizar `.help`:** Incluir el nuevo comando en la descripción del panel de ayuda.
* **[ ] Visualización en el inicio:** Modificar el mensaje de bienvenida para mostrar cuál es el modelo activo actualmente mediante `Config.get_model()`.