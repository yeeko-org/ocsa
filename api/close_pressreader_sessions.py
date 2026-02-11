#!/usr/bin/env python
"""
Script para cerrar todas las sesiones activas de PressReader.

Uso:
    python close_pressreader_sessions.py

Este script es útil cuando obtienes el error:
    "PressReader Status 2: Has excedido el número de sesiones simultáneas"

PressReader tiene un límite de sesiones activas simultáneas. Si intentas
hacer login y recibes Status 2, significa que hay otras sesiones abiertas
(por ejemplo, en el navegador o de ejecuciones previas del scraper).

Este script hace login con forceSignOut=true para cerrar automáticamente
todas las sesiones antiguas y poder crear una nueva.
"""

import os
import sys

import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from source.scraper.scraper_base import close_all_pressreader_sessions

if __name__ == "__main__":
    print("=" * 60)
    print("CERRAR SESIONES DE PRESSREADER")
    print("=" * 60)
    print()

    try:
        close_all_pressreader_sessions()
        print("\n" + "=" * 60)
        print("✓ SESIONES CERRADAS EXITOSAMENTE")
        print("=" * 60)
        print("\nAhora puedes ejecutar el scraper de Proceso:")
        print("  python test_proceso_scraper.py")
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")
        sys.exit(1)

    except ValueError as e:
        # Error esperado (Status 2 persistente, etc.)
        print("\n" + "=" * 60)
        print("❌ NO SE PUDIERON CERRAR LAS SESIONES")
        print("=" * 60)
        print(f"\nRazón: {str(e)}")
        print("\nEl problema debe resolverse manualmente.")
        sys.exit(1)

    except Exception as e:
        # Error inesperado
        print("\n" + "=" * 60)
        print("❌ ERROR INESPERADO")
        print("=" * 60)
        print(f"\n{str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
