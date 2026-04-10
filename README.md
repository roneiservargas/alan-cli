# 🚀 Alan AI CLI — v7.0 PRO

**Alan** es un asistente de IA de alto rendimiento diseñado para vivir en tu terminal. Inspirado en herramientas como Claude Code y Gemini CLI, Alan ofrece una interfaz fluida, manejo de contexto de archivos y una experiencia de usuario optimizada para desarrolladores.

---

## ✨ Características Principales

* **⚡ Interfaz Fluida:** Respuestas en streaming dentro de paneles elegantes con bordes redondeados.
* **📂 Contexto de Archivos:** Inyecta múltiples archivos directamente en el chat usando el comando `.file`.
* **💾 Extracción de Código:** Guarda el último bloque de código generado por la IA con un solo comando (`.save`).
* **🤖 Flexibilidad de Modelos:** Cambia entre modelos de OpenRouter en caliente con `.model`.
* **⌨️ Input Multilínea Pro:** * `Enter`: Enviar mensaje.
    * `Alt + Enter`: Nueva línea.
* **📱 Diseño Responsivo:** Manejo dinámico de señales (SIGWINCH) para adaptarse al cambio de tamaño de la terminal sin romper la visual.

---

## 🛠️ Instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/alan-cli.git
   cd alan-cli
   ```

2. **Instala en modo editable:**
   ```bash
   pip install -e .
   ```

---

## ⚙️ Configuración

Alan busca tu **API KEY** de OpenRouter y tus preferencias en el archivo `~/.alanrc`. Si el archivo no existe, puedes crearlo manualmente:

```bash
# ~/.alanrc
API_KEY=tu_api_key_aqui
MODEL=openrouter/auto
```

> **Nota:** También puedes exportar la clave como variable de entorno: `export ALAN_API_KEY='tu_clave'`.

---

## ⌨️ Comandos Disponibles

| Comando | Descripción |
| :--- | :--- |
| `.help` | Muestra el menú de ayuda con todos los comandos. |
| `.model` | Cambia el modelo de IA y guarda la preferencia en `~/.alanrc`. |
| `.file <f1> <f2> -- <prompt>` | Carga archivos como contexto para tu consulta. |
| `.save <nombre.ext>` | Extrae el último bloque de código y lo guarda en un archivo. |
| `.clear` | Limpia el historial de la sesión actual. |
| `.exit` | Cierra la sesión de Alan. |

---

## 🖥️ Uso de Archivos

Para trabajar con código existente, simplemente usa el comando `.file` seguido de los nombres de los archivos, un separador `--` y tu instrucción:

```text
Tú ❯ .file main.py utils.py -- Analiza estos archivos y optimiza la lógica de reintento.
```

---

## 🎨 Paleta de Colores
Alan utiliza una paleta basada en **Azul y Verde** para una legibilidad máxima en temas oscuros:
* **Tú:** Resaltado en Verde Cyan.
* **Alan:** Paneles con bordes Verdes y títulos Azules.
* **Sistema:** Mensajes de estado en Cyan dim.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

**Desarrollado con ❤️ por Roneiser Vargas**
