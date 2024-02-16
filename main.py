"""GitHub Organization License Audit Tool"""

from argparse import ArgumentParser,Namespace
import logging
import os
from tasks.export_licenses import DepsExporter

logger = logging.getLogger(__name__)

try:
    from ghastoolkit import (
        GitHub,
        DependencyGraph,
    )
except:
    print("Failed to load `ghastoolkit`")
    print("please install it")
    exit(1)

class CLI():
    def __init__(self):
        self.parser = ArgumentParser("gh org-license-audit")
        
        ghas_toolkit_parser = ArgumentParser(add_help=False)
        ghas_toolkit_parser.add_argument(
            "--debug", 
            dest="debug",
            action="store_true",
            help="Enable Debugging"
        )
        ghas_toolkit_parser.add_argument(
            "-t",
            "--github-token",
            dest="token",
            default=os.environ.get("GITHUB_TOKEN"),
            help="GitHub API Token (default: GITHUB_TOKEN)",
        )

        subparsers = self.parser.add_subparsers(dest="operation")

        self.exportParser = subparsers.add_parser("export-licenses", parents=[ghas_toolkit_parser])
        self.exportParser.add_argument(
            "--csv", 
            help="The name of the output file",
            dest="csv",
            default="dependencies.csv")
        self.exportParser.add_argument(
            "-o",
            "--github-org", 
            dest="owner",
            required=True,
            help="The Organization to export the CSV for"
        )


    def parse_args(self):
        """Parse Arguments and set Log-Level"""
        arguments = self.parser.parse_args()
        logging.basicConfig(
            level=(
                logging.DEBUG
                if arguments.debug or os.environ.get("DEBUG")
                else logging.INFO
            ),
            format="%(message)s",
        )
        return arguments

    def run(self, arguments: Namespace):
        if arguments.operation == "export-licenses":
            GitHub.init(
                ## Workaround as "owner" is currently not working in GHAS Toolkit
                ## The Repo name doesn't matter as we are only using functions that use the owner
                repository=arguments.owner + "/dontcare",
                owner=arguments.owner,
                token=arguments.token
            )
            write_dependencies_to_csv(arguments.csv, arguments.owner)


def write_dependencies_to_csv(target_csv, organization):
    """Writes all found dependencies with a count to a CSV File"""
    deps_exporter = DepsExporter(DependencyGraph(), organization)
    deps_exporter.run(target_csv)

if __name__ == "__main__":
    try:
        cli = CLI()
        cli.run(cli.parse_args())
    except Exception as err:
        logger.error(err)
        exit(1)
