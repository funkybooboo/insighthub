import typer
from insighthub_cli.commands import docs, rag, fetch, auth

app = typer.Typer(help="Insighthub CLI")

app.add_typer(auth.app, name="auth")
app.add_typer(docs.app, name="docs")
app.add_typer(rag.app, name="rag")
app.add_typer(fetch.app, name="fetch")

if __name__ == "__main__":
    app()
