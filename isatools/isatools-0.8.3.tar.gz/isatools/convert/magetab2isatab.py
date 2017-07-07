from isatools import isatab
import os
import logging
from isatools.magetab import MageTabParser
import isatools

logging.basicConfig(level=isatools.log_level)
LOG = logging.getLogger(__name__)


def convert(idf_file_path, output_path):
    """ Converter for MAGE-TAB to ISA-Tab
    :param idf_file_path: File descriptor of input IDF file
    :param output_path: Path to directory to write output ISA-Tab files to
    """
    parser = MageTabParser()
    parser.parse_idf(idf_file_path)
    sdrf_files = [x.value for x in parser.ISA.studies[-1].comments if 'SDRF File' in x.name]
    if len(sdrf_files) == 1:
        sdrf_files = sdrf_files[0].split(';')
        for sdrf_file in sdrf_files:
            table_files = parser.parse_sdrf_to_isa_table_files(os.path.join(os.path.dirname(idf_file_path), sdrf_file))
            for in_fp in table_files:
                LOG.info("Writing {0} to {1}".format(in_fp.name, output_path))
                with open(os.path.join(output_path, in_fp.name), 'w') as out_fp:
                    out_fp.write(in_fp.read())
    LOG.info("Writing {0} to {1}".format("i_investigation.txt", output_path))
    isatab.dump(parser.ISA, output_path=output_path, skip_dump_tables=True)