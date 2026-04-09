#! /bin/python3
import os
import requests
import json
import sys
import re
from typing import List, Dict, Optional

# TUI Libraries
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import NestedCompleter, PathCompleter
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style as PtStyle
from prompt_toolkit.key_binding import KeyBindings
from pygments.lexer import RegexLexer
from pygments.token import Keyword, Operator, Text

from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rich.panel import Panel
from rich import box

# --- CONFIGURACIÓN Y CONSTANTES ---
class Config:
    URL_API = "https://openrouter.ai/api/v1/chat/completions"
    HISTORY_FILE = ".alan_history"
    CONFIG_FILE = os.path.expanduser("~/.alanrc")

    @classmethod
    def get_model(cls) -> str:
        env_model = os.getenv("ALAN_MODEL")
        if env_model:
            return env_model

        if os.path.exists(cls.CONFIG_FILE):
            try:
                with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("MODEL="):
                            return line.split("=", 1)[1].strip()
            except Exception as e:
                Console().print(f"[red]❌ Error leyendo {cls.CONFIG_FILE}: {e}[/red]")

        return "openrouter/auto"

    @classmethod
    def set_model(cls, model_name: str):
        lines = []

        if os.path.exists(cls.CONFIG_FILE):
            try:
                with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except Exception:
                pass

        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith("MODEL="):
                lines[i] = f"MODEL={model_name}\n"
                updated = True
                break

        if not updated:
            lines.append(f"MODEL={model_name}\n")

        try:
            with open(cls.CONFIG_FILE, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception as e:
            Console().print(f"[red]❌ Error escribiendo {cls.CONFIG_FILE}: {e}[/red]")

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        api_key = os.getenv("ALAN_API_KEY")
        if api_key:
            return api_key
        
        if os.path.exists(cls.CONFIG_FILE):
            try:
                with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("API_KEY="):
                            return line.split("=", 1)[1].strip()
            except Exception as e:
                Console().print(f"[red]❌ Error leyendo {cls.CONFIG_FILE}: {e}[/red]")
        return None

# --- LÓGICA DE IA ---
class AIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.messages = [
            {"role": "system", "content": ""}
        ]

    def clear_history(self):
        self.messages = [self.messages[0]]

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_last_assistant_response(self) -> Optional[str]:
        for msg in reversed(self.messages):
            if msg['role'] == 'assistant':
                return msg['content']
        return None

    def stream_chat(self, user_input: str):
        self.add_message("user", user_input)
        payload = {
            "model": Config.get_model(),
            "messages": self.messages,
            "stream": True
        }
        return requests.post(Config.URL_API, headers=self.headers, json=payload, stream=True)

# --- INTERFAZ DE USUARIO (TUI) ---
class AlanLexer(RegexLexer):
    tokens = {
        'root': [
            (r'^\.(file|exit|clear|save|help|model)\b', Keyword.Reserved),
            (r'--', Operator),
            (r'.', Text),
        ]
    }

class ChatInterface:
    def __init__(self, ai_client: AIClient):
        self.ai = ai_client
        self.console = Console()
        self.input_style = PtStyle.from_dict({
            'pygments.keyword.reserved': '#00ffaa bold',
            'pygments.operator': '#00aaff bold',
        })
        self.completer = NestedCompleter.from_nested_dict({
            '.exit': None,
            '.clear': None,
            '.help': None,
            '.model': None,
            '.save': PathCompleter(expanduser=True), 
            '.file': PathCompleter(expanduser=True)
        })

    def print_panel(self, text, title="Alan", style="blue", box_style=box.ROUNDED):
        self.console.print(Panel(text, title=title, border_style=style, box=box_style))

    def handle_model(self):
        model_name = prompt("🤖 Ingresa el modelo (ej: anthropic/claude-3-opus): ").strip()

        if not model_name:
            self.console.print("[red]❌ Modelo inválido.[/red]")
            return

        Config.set_model(model_name)

        self.print_panel(
            f"[bold green]✔ Modelo cambiado a:[/bold green]\n[cyan]{model_name}[/cyan]",
            title="Modelo actualizado",
            style="green"
        )

    def handle_save(self, user_input: str):
        filename = user_input[6:].strip()
        if not filename:
            self.console.print("[red]❌ Especifica un nombre de archivo.[/red]")
            return

        content = self.ai.get_last_assistant_response()
        if not content:
            self.console.print("[red]❌ No hay respuestas previas para guardar.[/red]")
            return

        blocks = re.findall(r"```[^\n]*\n(.*?)```", content, re.DOTALL)
        if not blocks:
            self.console.print("[yellow]⚠️ No se encontraron bloques de código.[/yellow]")
            return

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(blocks[-1].strip() + "\n")
            self.console.print(f"[bold green]💾 Guardado en [blue]{filename}[/blue][/bold green]")
        except Exception as e:
            self.console.print(f"[red]❌ Error al guardar: {e}[/red]")

    def handle_file(self, user_input: str) -> Optional[str]:
        if "--" not in user_input:
            self.console.print("[red]❌ Sintaxis: .file archivo1.py archivo2.py -- instrucción[/red]")
            return None

        files_part, instruction = user_input.split("--", 1)
        filenames = files_part[6:].strip().split()
        context = "Archivos proporcionados:\n\n"
        
        try:
            for name in filenames:
                with open(name, 'r', encoding='utf-8') as f:
                    context += f"### Archivo: `{name}`\n```\n{f.read()}\n```\n\n"
                self.console.print(f"[green]✔ '{name}' cargado.[/green]")
            return f"{context}---\n**Instrucción:** {instruction.strip()}"
        except Exception as e:
            self.console.print(f"[red]❌ Error leyendo archivos: {e}[/red]")
            return None

    def run(self):
        self.print_panel(
            f"[bold green]Sistema iniciado.[/bold green]\n"
            f"Modelo activo: [cyan]{Config.get_model()}[/cyan]\n"
            f"Escribe [bold cyan].help[/bold cyan] para comandos.",
            title="🚀 ALAN AI - TERMINAL v7.0 PRO",
            style="blue"
        )

        kb = KeyBindings()

        @kb.add('enter')
        def _(event):
            event.current_buffer.validate_and_handle()

        @kb.add('escape', 'enter')
        def _(event):
            event.current_buffer.insert_text('\n')

        while True:
            try:
                user_input = prompt(
                    "\nTú ❯ ", 
                    history=FileHistory(Config.HISTORY_FILE),
                    completer=self.completer,
                    lexer=PygmentsLexer(AlanLexer),
                    style=self.input_style,
                    multiline=True,
                    key_bindings=kb
                ).strip()

                if not user_input:
                    continue

                cmd = user_input.lower()

                if cmd == ".exit":
                    self.print_panel("Cerrando Alan. ¡Hasta pronto!", style="red")
                    break

                elif cmd == ".help":
                    self.print_panel(
                        "[cyan].help[/cyan] -> Menú\n"
                        "[cyan].exit[/cyan] -> Salir\n"
                        "[cyan].clear[/cyan] -> Limpiar chat\n"
                        "[cyan].model[/cyan] -> Cambiar modelo\n"
                        "[cyan].file <f1> <f2> -- <prompt>[/cyan] -> Contexto archivos\n"
                        "[cyan].save <archivo>[/cyan] -> Guardar código\n\n"
                        "[dim]* Tip: [Enter] para enviar, [Alt+Enter] para nueva línea.[/dim]",
                        title="📖 Comandos",
                        style="cyan"
                    )
                    continue

                elif cmd == ".clear":
                    self.ai.clear_history()
                    self.console.print("[bold green]✨ Historial limpiado.[/bold green]")
                    continue

                elif cmd == ".model":
                    self.handle_model()
                    continue

                elif cmd.startswith(".save "):
                    self.handle_save(user_input)
                    continue

                elif cmd.startswith(".file "):
                    processed_input = self.handle_file(user_input)
                    if not processed_input:
                        continue
                    user_input = processed_input

                with self.console.status("[bold green]Procesando...[/bold green]", spinner="bouncingBar"):
                    response = self.ai.stream_chat(user_input)

                if response.status_code == 200:
                    full_text = ""
                    with Live(
                        Panel(Markdown(""), title="Alan", border_style="green", box=box.ROUNDED),
                        console=self.console,
                        refresh_per_second=15
                    ) as live:
                        for line in response.iter_lines():
                            if not line:
                                continue
                            decoded = line.decode('utf-8').replace('data: ', '')
                            if decoded == '[DONE]':
                                break
                            try:
                                data = json.loads(decoded)
                                content = data['choices'][0]['delta'].get('content', '')
                                full_text += content
                                live.update(
                                    Panel(Markdown(full_text), title="Alan", border_style="green", box=box.ROUNDED)
                                )
                            except json.JSONDecodeError:
                                continue

                    self.ai.add_message("assistant", full_text)
                else:
                    self.console.print(f"[red]❌ API Error {response.status_code}: {response.text}[/red]")

            except (KeyboardInterrupt, EOFError):
                break
            except Exception as e:
                self.console.print(f"[bold red]❌ Error inesperado: {e}[/bold red]")

# --- PUNTO DE ENTRADA PARA EL SCRIPT 'alan' ---
def chat():
    key = Config.get_api_key()
    if not key:
        Console().print("[bold red]❌ Error: No se encontró API_KEY en env o ~/.alanrc[/bold red]")
        sys.exit(1)
    
    client = AIClient(key)
    app = ChatInterface(client)
    app.run()

if __name__ == "__main__":
    chat()
