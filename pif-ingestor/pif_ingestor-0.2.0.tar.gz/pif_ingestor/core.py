from .ui import get_cli
from .manager import IngesterManager
from .enrichment import add_tags, add_license, add_contact
from .uploader import upload
from .packager import create_package
import os.path
from os import walk
from pypif import pif
import logging


def _handle_pif(path, ingest_name, convert_args, enrich_args, ingest_manager):
    """Ingest and enrich pifs from a path, returning affected paths"""
    # Run an ingest extension
    pifs = ingest_manager.run_extension(ingest_name, path, convert_args)

    # Perform enrichment
    add_tags(pifs, enrich_args['tags'])
    add_license(pifs, enrich_args['license'])
    add_contact(pifs, enrich_args['contact'])

    # Write the pif
    if os.path.isfile(path):
        pif_name = "{}_{}".format(path, "pif.json")
        res = [path, pif_name]
    else:
        pif_name = os.path.join(path, "pif.json")
        res = [path]

    with open(pif_name, "w") as f:
        pif.dump(pifs, f, indent=2)
    logging.info("Created pif at {}".format(pif_name))

    return res


def main(args):
    """Main driver for pif-ingestor"""

    enrichment_args = {
        'tags':    args.tags,
        'license': args.license,
        'contact': args.contact
    }

    # Load the ingest extensions
    ingest_manager = IngesterManager()

    all_files = []
    exceptions = {}
    if args.recursive:
        for root, dirs, files in walk(args.path):
            try:
                new = _handle_pif(root, args.format, args.converter_arguments, enrichment_args, ingest_manager)
                all_files.extend(new)
            except Exception as err:
                exceptions[root] = err
    else:
        all_files.extend(_handle_pif(args.path, args.format, args.converter_arguments, enrichment_args, ingest_manager))

    if len(all_files) == 0 and len(exceptions) > 0:
        raise ValueError("Unable to parse any subdirectories.  Exceptions:\n{}".format(
            "\n".join(["{}: {}".format(k, str(v)) for k, v in exceptions]))
        )

    with open("ingestor.log", "w") as f:
        f.write("Exceptions:\n")
        for root, err in exceptions.items():
            f.write("{}: {}\n".format(root, str(err)))

    # Upload the pif and associated files
    if args.dataset:
        upload(all_files, args.dataset)

    if args.zip:
        if args.zip[-4:] == ".zip":
            zipname = args.zip
        else:
            zipname = args.zip + ".zip"
        create_package(all_files, zipname, format="zip")

    if args.tar:
        if args.tar[-4:] == ".tar":
            tarname = args.tar
        else:
            tarname = args.tar + ".tar"
        create_package(all_files, tarname, format="tar")
