# 🚀 Alan - AI Terminal Assistant

**Alan** es una interfaz de línea de comandos (CLI) potente, ligera y elegante construida en Python para interactuar con modelos de inteligencia artificial a través de la API de **OpenRouter**. 

Diseñado específicamente para ser compatible con entornos móviles como **Pydroid 3** y terminales de escritorio, Alan permite inyectar contexto de archivos locales directamente en tus conversaciones con la IA.

## ✨ Características

- 🆓 **Acceso Gratuito**: Configurado por defecto para usar modelos gratuitos de OpenRouter (`openrouter/auto`).
- 📁 **Inyección de Archivos**: Envía el contenido de archivos locales (`.py`, `.js`, `.html`, `.txt`, etc.) como contexto mediante comandos.
- 📂 **Soporte Multi-archivo**: Capacidad para cargar múltiples archivos simultáneamente usando un delimitador.
- ⚡ **Streaming**: Respuestas en tiempo real palabra por palabra.
- 🌀 **Interfaz Animada**: Spinner de carga y colores ANSI para una experiencia visual superior.
- 🧠 **Memoria de Sesión**: Mantiene el contexto de la conversación hasta que decidas limpiarlo.

## 🛠️ Instalación

1. **Clona o descarga** el repositorio.
2. Asegúrate de tener instalado **Python 3.x**.
3. Instala la única dependencia necesaria:
```bash
pip install requests
```
## 🚀 Configuración y Uso

1.  Abre el archivo `alan.py` con tu editor de texto.
    
2.  Sustituye el valor de `API_KEY` por tu llave de [OpenRouter](https://openrouter.ai/).
 
```python
API_KEY = "tu_api_key_aquí" 
```

3.  Ejecuta el programa:
```Bash
python alan.py    
```

## ⌨️ Comandos Disponibles

Dentro del chat, puedes usar los siguientes comandos especiales:
|**Comando**|**Descripción**|
|--|--|
|`.exit`|Cierra la aplicación de forma segura.|
|`.clear`|Limpia el historial de la conversación actual.|
|`.file <nombre> <instrucción>`| Lee un archivo y lo envía junto a tu pregunta.|
|`.files <f1> <f2> -- <instrucción>`|Carga varios archivos separados por el delimitador `--`.|

### Ejemplos de uso:

-   **Análisis de código:**
`.file script.py explica qué hace esta función`
    
-   **Análisis de proyecto (Multi-archivo):**
` .files index.html style.css -- ¿Por qué no se ve el fondo rojo?`

## 📝 Requisitos

-   Conexión a Internet.
    
-   Una API Key válida de OpenRouter.
    
-   Librería `requests`.

_Desarrollado con ❤️ para la comunidad de desarrolladores en movilidad._
