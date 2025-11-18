import typer
from rich import print

app = typer.Typer(help="Authentication commands")

@app.command()
def login(token: str = typer.Option(..., prompt=True, hide_input=True)):
    """Save API token locally."""
    # mock behavior
    print(f"[green]Logged in with token:[/green] {token[:4]}****")
