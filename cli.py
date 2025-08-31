"""
cli.py
Command-line interface for P2P Notes App.
Provides interactive note management and status display.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from models import Note
import time
import asyncio

def show_notes(notes_manager):
    console = Console()
    if not notes_manager:
        console.print("[yellow]📝 No notes yet. Create your first note![/yellow]")
        return
    table = Table(title="📋 Your Notes")
    table.add_column("#", style="cyan", width=3)
    table.add_column("Content", style="white")
    table.add_column("Updated", style="dim")
    sorted_notes = sorted(notes_manager.values(), key=lambda n: n.updated_at, reverse=True)
    for i, note in enumerate(sorted_notes, 1):
        content = note.content[:50] + "..." if len(note.content) > 50 else note.content
        updated = time.strftime("%H:%M:%S", time.localtime(note.updated_at))
        table.add_row(str(i), content, updated)
    console.print(table)

def show_status(device_id, notes_manager, peer_manager):
    console = Console()
    status = f"Device: {device_id} | Notes: {len(notes_manager)} | Peers: {len(peer_manager.peers)}"
    console.print(Panel(status, title="Status", border_style="green"))
    if peer_manager.peers:
        console.print("🌐 Connected peers:")
        for peer in peer_manager.peers:
            console.print(f"  • {peer}")

async def run_cli(device_id, notes_manager, peer_manager, db_manager):
    console = Console()
    while True:
        # Reload notes from DB to ensure latest view
        notes_manager.clear()
        notes_manager.update(db_manager.load_notes())
        console.print("\n" + "=" * 60)
        show_status(device_id, notes_manager, peer_manager)
        console.print()
        show_notes(notes_manager)
        console.print("\n[bold]Commands:[/bold]")
        console.print("1. [green]add[/green] - Add a new note")
        console.print("2. [blue]edit[/blue] - Edit a note")
        console.print("3. [red]delete[/red] - Delete a note")
        console.print("4. [yellow]refresh[/yellow] - Refresh view")
        console.print("5. [magenta]quit[/magenta] - Exit")
        try:
            cmd = await asyncio.get_event_loop().run_in_executor(
                None, Prompt.ask, "\n[bold]Enter command"
            )
            if cmd.lower() in ['add', '1']:
                content = await asyncio.get_event_loop().run_in_executor(
                    None, Prompt.ask, "Enter note content"
                )
                if content:
                    note = Note(content=content)
                    db_manager.save_note(note)
                    notes_manager.clear()
                    notes_manager.update(db_manager.load_notes())
                    console.print(f"[green]✅ Note added![/green]")
            elif cmd.lower() in ['edit', '2']:
                if not notes_manager:
                    console.print("[red]No notes to edit[/red]")
                    continue
                note_num = await asyncio.get_event_loop().run_in_executor(
                    None, Prompt.ask, "Enter note number to edit"
                )
                try:
                    sorted_notes = sorted(notes_manager.values(), key=lambda n: n.updated_at, reverse=True)
                    note = sorted_notes[int(note_num) - 1]
                    console.print(f"Current content: {note.content}")
                    new_content = await asyncio.get_event_loop().run_in_executor(
                        None, Prompt.ask, "Enter new content (or press Enter to keep current)"
                    )
                    if new_content:
                        note.content = new_content
                        note.updated_at = time.time()
                        db_manager.save_note(note)
                        notes_manager.clear()
                        notes_manager.update(db_manager.load_notes())
                        console.print("[green]✅ Note updated![/green]")
                except (ValueError, IndexError):
                    console.print("[red]Invalid note number[/red]")
            elif cmd.lower() in ['delete', '3']:
                if not notes_manager:
                    console.print("[red]No notes to delete[/red]")
                    continue
                note_num = await asyncio.get_event_loop().run_in_executor(
                    None, Prompt.ask, "Enter note number to delete"
                )
                try:
                    sorted_notes = sorted(notes_manager.values(), key=lambda n: n.updated_at, reverse=True)
                    note = sorted_notes[int(note_num) - 1]
                    db_manager.delete_note(note.id)
                    notes_manager.clear()
                    notes_manager.update(db_manager.load_notes())
                    console.print("[red]🗑️ Note deleted![/red]")
                except (ValueError, IndexError):
                    console.print("[red]Invalid note number[/red]")
            elif cmd.lower() in ['refresh', '4']:
                notes_manager.clear()
                notes_manager.update(db_manager.load_notes())
                continue
            elif cmd.lower() in ['quit', 'exit', '5']:
                break
            else:
                console.print("[red]Unknown command[/red]")
        except KeyboardInterrupt:
            break