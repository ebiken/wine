import typer
from app.cli.import_cmd import import_seed

app = typer.Typer(help="WineDB management CLI")

# Dummy callback keeps Typer from collapsing a single subcommand into the root
@app.callback()
def _main() -> None:
    pass

app.command("import")(import_seed)

if __name__ == "__main__":
    app()
