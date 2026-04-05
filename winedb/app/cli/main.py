import typer
from app.cli.import_cmd import import_seed

app = typer.Typer(help="WineDB management CLI")
app.command("import")(import_seed)

if __name__ == "__main__":
    app()
