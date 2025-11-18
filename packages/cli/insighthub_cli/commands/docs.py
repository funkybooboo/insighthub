import typer
from rich import print

app = typer.Typer(help="Document processing commands")

@app.command()
def upload(path: str):
    """Upload a document to be processed."""
    print(f"[cyan]Uploading[/cyan] {path} ...")
    # mock: you would actually hit your API here
    print("[green]Document uploaded and queued[/green]")
