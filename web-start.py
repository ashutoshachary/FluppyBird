import asyncio
import pygame
import platform
import sys

async def main():
    # Check if running in a web environment
    is_web = False
    try:
        import pyodide
        is_web = True
    except ImportError:
        pass
    
    if is_web:
        # Special handling for web context
        await asyncio.sleep(0.1)
    
    # Import and run the game
    from main import run_game
    run_game()

if __name__ == "__main__":
    asyncio.run(main())