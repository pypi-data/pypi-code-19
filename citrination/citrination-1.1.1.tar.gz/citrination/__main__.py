import command_router
from citrination.commands import upload
from citrination.commands import create_dataset_version
from citrination.commands import create_dataset
from citrination.commands import update_dataset
from citrination.commands import get_pif
from citrination.commands import get_files
from citrination.commands import get_file

app = command_router.CommandRouter()
app.register(upload.App, ['upload'])
app.register(create_dataset.App, ['create_dataset'])
app.register(update_dataset.App, ['update_dataset'])
app.register(create_dataset_version.App, ['create_dataset_version'])
app.register(get_pif.App, ['get_pif'])
app.register(get_files.App, ['get_files'])
app.register(get_file.App, ['get_file'])


def main():
    """
    Run the application.
    """
    app.run()

if __name__ == "__main__":
    main()
