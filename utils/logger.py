
from rich.console import Console
console = Console()
def log_pass(msg): console.print(f"[green]✔[/green] {msg}")
def log_fail(msg): console.print(f"[red]✘[/red] {msg}")
def log_warn(msg): console.print(f"[yellow]⚠[/yellow] {msg}")
