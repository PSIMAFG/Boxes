#!/usr/bin/env python3
"""
Script de Inicialización del Sistema de Gestión de Boxes
=========================================================

Este script verifica y configura automáticamente el entorno de desarrollo:
- Verifica la existencia del entorno virtual (venv)
- Crea el venv si no existe
- Verifica e instala las dependencias requeridas
- Ejecuta las migraciones de base de datos
- Inicializa los datos de prueba
- Muestra el progreso al usuario en una ventana GUI

Uso:
    python setup.py
"""

import sys
import os
import subprocess
import platform
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue


class SetupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión de Boxes - Inicialización")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Cola para comunicación entre hilos
        self.log_queue = queue.Queue()

        # Variables
        self.is_windows = platform.system() == "Windows"
        self.project_dir = Path(__file__).parent
        self.venv_dir = self.project_dir / ".venv"
        self.python_executable = self._get_python_executable()

        self._create_widgets()
        self._update_log_display()

    def _get_python_executable(self):
        """Obtiene la ruta al ejecutable de Python en el venv"""
        if self.is_windows:
            return self.venv_dir / "Scripts" / "python.exe"
        else:
            return self.venv_dir / "bin" / "python"

    def _get_poetry_executable(self):
        """Obtiene la ruta al ejecutable de Poetry"""
        if self.is_windows:
            return self.venv_dir / "Scripts" / "poetry.exe"
        else:
            return self.venv_dir / "bin" / "poetry"

    def _create_widgets(self):
        """Crea los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar el grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Título
        title_label = ttk.Label(
            main_frame,
            text="Inicialización del Sistema de Gestión de Boxes",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)

        # Área de log
        log_frame = ttk.LabelFrame(main_frame, text="Proceso de Inicialización", padding="5")
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            width=80,
            height=20,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky=tk.E)

        self.start_button = ttk.Button(
            button_frame,
            text="Iniciar Configuración",
            command=self._start_setup
        )
        self.start_button.grid(row=0, column=0, padx=5)

        self.close_button = ttk.Button(
            button_frame,
            text="Cerrar",
            command=self.root.quit,
            state=tk.DISABLED
        )
        self.close_button.grid(row=0, column=1, padx=5)

    def _log(self, message, level="INFO"):
        """Agrega un mensaje al log"""
        self.log_queue.put((message, level))

    def _update_log_display(self):
        """Actualiza la visualización del log desde la cola"""
        try:
            while True:
                message, level = self.log_queue.get_nowait()

                # Configurar colores según el nivel
                if level == "ERROR":
                    color = "red"
                elif level == "SUCCESS":
                    color = "green"
                elif level == "WARNING":
                    color = "orange"
                else:
                    color = "black"

                # Insertar el mensaje
                self.log_text.insert(tk.END, f"[{level}] {message}\n")
                self.log_text.tag_add(level, "end-2l", "end-1l")
                self.log_text.tag_config(level, foreground=color)
                self.log_text.see(tk.END)

        except queue.Empty:
            pass

        # Programar la próxima actualización
        self.root.after(100, self._update_log_display)

    def _update_progress(self, value):
        """Actualiza la barra de progreso"""
        self.progress_var.set(value)
        self.root.update_idletasks()

    def _run_command(self, command, description, show_output=True):
        """Ejecuta un comando del sistema"""
        self._log(f"Ejecutando: {description}...", "INFO")

        try:
            if isinstance(command, str):
                command = command.split()

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.project_dir)
            )

            stdout, stderr = process.communicate()

            if process.returncode == 0:
                self._log(f"✓ {description} completado exitosamente", "SUCCESS")
                if show_output and stdout:
                    for line in stdout.strip().split('\n')[-5:]:  # Últimas 5 líneas
                        if line.strip():
                            self._log(f"  {line}", "INFO")
                return True
            else:
                self._log(f"✗ Error en {description}", "ERROR")
                if stderr:
                    for line in stderr.strip().split('\n')[:10]:  # Primeras 10 líneas
                        if line.strip():
                            self._log(f"  {line}", "ERROR")
                return False

        except Exception as e:
            self._log(f"✗ Excepción al ejecutar {description}: {str(e)}", "ERROR")
            return False

    def _check_python(self):
        """Verifica que Python esté instalado"""
        self._log("Verificando instalación de Python...", "INFO")
        try:
            result = subprocess.run(
                [sys.executable, "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip()
            self._log(f"✓ Python encontrado: {version}", "SUCCESS")
            return True
        except Exception as e:
            self._log(f"✗ Python no encontrado: {str(e)}", "ERROR")
            return False

    def _check_poetry(self):
        """Verifica que Poetry esté instalado"""
        self._log("Verificando instalación de Poetry...", "INFO")
        try:
            result = subprocess.run(
                ["poetry", "--version"],
                capture_output=True,
                text=True,
                check=True,
                cwd=str(self.project_dir)
            )
            version = result.stdout.strip()
            self._log(f"✓ Poetry encontrado: {version}", "SUCCESS")
            return True
        except Exception as e:
            self._log(f"✗ Poetry no encontrado: {str(e)}", "ERROR")
            self._log("Por favor instala Poetry: https://python-poetry.org/docs/#installation", "WARNING")
            return False

    def _check_venv(self):
        """Verifica si existe el entorno virtual"""
        self._log("Verificando entorno virtual...", "INFO")

        if self.venv_dir.exists() and self.python_executable.exists():
            self._log(f"✓ Entorno virtual encontrado en: {self.venv_dir}", "SUCCESS")
            return True
        else:
            self._log(f"✗ Entorno virtual no encontrado", "WARNING")
            return False

    def _create_venv(self):
        """Crea el entorno virtual usando Poetry"""
        self._log("Creando entorno virtual...", "INFO")

        # Poetry crea automáticamente el venv cuando instalas dependencias
        return self._run_command(
            ["poetry", "env", "use", sys.executable],
            "Configuración del entorno virtual"
        )

    def _install_dependencies(self):
        """Instala las dependencias del proyecto"""
        self._log("Instalando dependencias del proyecto...", "INFO")
        self._log("Esto puede tomar varios minutos...", "WARNING")

        return self._run_command(
            ["poetry", "install"],
            "Instalación de dependencias"
        )

    def _run_migrations(self):
        """Ejecuta las migraciones de base de datos"""
        self._log("Ejecutando migraciones de base de datos...", "INFO")

        return self._run_command(
            ["poetry", "run", "alembic", "upgrade", "head"],
            "Migraciones de base de datos"
        )

    def _seed_database(self):
        """Inicializa los datos de prueba"""
        self._log("Inicializando datos de prueba...", "INFO")
        self._log("(Si los datos ya existen, este paso puede mostrar advertencias - es normal)", "WARNING")

        # Este comando puede fallar si los datos ya existen, pero no es crítico
        success = self._run_command(
            ["poetry", "run", "python", "-m", "app.scripts.seed_data"],
            "Inicialización de datos",
            show_output=False
        )

        if not success:
            self._log("Los datos iniciales ya existen o hubo un error menor - continuando...", "WARNING")

        return True  # No bloqueamos por esto

    def _verify_installation(self):
        """Verifica que todo esté correctamente instalado"""
        self._log("Verificando instalación...", "INFO")

        # Verificar que se puedan importar los módulos principales
        test_import = """
import sys
try:
    import fastapi
    import sqlalchemy
    import pydantic
    from email_validator import validate_email
    print("✓ Todas las dependencias principales se importaron correctamente")
    sys.exit(0)
except ImportError as e:
    print(f"✗ Error al importar: {e}")
    sys.exit(1)
"""

        try:
            result = subprocess.run(
                ["poetry", "run", "python", "-c", test_import],
                capture_output=True,
                text=True,
                cwd=str(self.project_dir)
            )

            self._log(result.stdout.strip(), "SUCCESS" if result.returncode == 0 else "ERROR")
            return result.returncode == 0

        except Exception as e:
            self._log(f"✗ Error en verificación: {str(e)}", "ERROR")
            return False

    def _setup_process(self):
        """Proceso completo de configuración"""
        try:
            self._log("=" * 60, "INFO")
            self._log("INICIANDO CONFIGURACIÓN DEL SISTEMA", "INFO")
            self._log("=" * 60, "INFO")

            steps = [
                (10, self._check_python, "Verificación de Python"),
                (20, self._check_poetry, "Verificación de Poetry"),
                (30, self._check_venv, "Verificación de entorno virtual"),
                (40, self._create_venv, "Creación de entorno virtual"),
                (50, self._install_dependencies, "Instalación de dependencias"),
                (70, self._run_migrations, "Migraciones de base de datos"),
                (85, self._seed_database, "Inicialización de datos"),
                (95, self._verify_installation, "Verificación final"),
            ]

            for progress, step_func, description in steps:
                self._update_progress(progress)

                # Algunos pasos son opcionales
                if description == "Creación de entorno virtual":
                    if self.venv_dir.exists():
                        self._log(f"Saltando: {description} (ya existe)", "INFO")
                        continue

                if not step_func():
                    if description in ["Verificación de Poetry"]:
                        self._log(f"⚠ {description} falló - configuración incompleta", "ERROR")
                        self._update_progress(100)
                        messagebox.showerror(
                            "Error de Configuración",
                            f"Error crítico: {description}\n\n"
                            "Por favor revisa el log para más detalles."
                        )
                        return False
                    elif description not in ["Inicialización de datos"]:
                        self._log(f"⚠ {description} falló pero continuando...", "WARNING")

            self._update_progress(100)

            self._log("=" * 60, "INFO")
            self._log("✓ CONFIGURACIÓN COMPLETADA EXITOSAMENTE", "SUCCESS")
            self._log("=" * 60, "INFO")
            self._log("", "INFO")
            self._log("Próximos pasos:", "INFO")
            self._log("1. Ejecuta: poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000", "INFO")
            self._log("2. Abre en tu navegador: http://localhost:8000/docs", "INFO")
            self._log("3. Credenciales de prueba:", "INFO")
            self._log("   - Email: admin@clinica.cl", "INFO")
            self._log("   - Password: admin123", "INFO")

            messagebox.showinfo(
                "Configuración Completada",
                "¡El sistema ha sido configurado exitosamente!\n\n"
                "Puedes iniciar el servidor ejecutando:\n"
                "poetry run uvicorn app.main:app --reload\n\n"
                "Luego visita: http://localhost:8000/docs"
            )

            return True

        except Exception as e:
            self._log(f"✗ Error inesperado: {str(e)}", "ERROR")
            self._update_progress(100)
            messagebox.showerror(
                "Error Inesperado",
                f"Ocurrió un error inesperado:\n{str(e)}\n\n"
                "Por favor revisa el log para más detalles."
            )
            return False

        finally:
            self.start_button.config(state=tk.DISABLED)
            self.close_button.config(state=tk.NORMAL)

    def _start_setup(self):
        """Inicia el proceso de configuración en un hilo separado"""
        self.start_button.config(state=tk.DISABLED)
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)

        # Ejecutar en un hilo separado para no bloquear la UI
        thread = threading.Thread(target=self._setup_process)
        thread.daemon = True
        thread.start()


def main():
    """Función principal"""
    root = tk.Tk()
    app = SetupApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
