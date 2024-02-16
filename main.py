"""GitHub Organization License Audit Tool"""

from argparse import ArgumentParser,Namespace
import logging
import os
import csv
from tasks.export_licenses import DepsExporter
from tasks.aggregate_licenses import aggregate_license

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
        
        debug_parser = ArgumentParser(add_help=False)
        debug_parser.add_argument(
            "--debug", 
            dest="debug",
            action="store_true",
            help="Enable Debugging"
        )

        token_parser = ArgumentParser(add_help=False)
        token_parser.add_argument(
            "-t",
            "--github-token",
            dest="token",
            default=os.environ.get("GITHUB_TOKEN"),
            help="GitHub API Token (default: GITHUB_TOKEN)",
        )

        subparsers = self.parser.add_subparsers(dest="operation")

        self.export_deps_parser = subparsers.add_parser("export-deps", parents=[debug_parser, token_parser], help="Export a list of all Dependencies in your organizations, their licenses and a count in how many repositories this is present to a CSV File." )
        self.export_deps_parser.add_argument(
            "--target-csv", 
            help="The name of the output file",
            dest="csv",
            default="dependencies.csv"
        )

        self.export_deps_parser.add_argument(
            "-o",
            "--github-org", 
            dest="owner",
            required=True,
            help="The Organization to export the CSV for"
        )
        
        self.aggregate_licenses = subparsers.add_parser(
            "aggregate-licenses", 
            parents=[debug_parser],
            help="Create a new CSV with the aggregated licenses from a previous run of `export-deps`"
        )
        
        self.aggregate_licenses.add_argument(
            "--source-csv",
            dest="source_csv",
            default="dependencies.csv",
            help="The CSV created by `export-deps` to read from"
        )
        self.aggregate_licenses.add_argument(
            "--target-csv",
            dest="target_csv",
            default="licenses.csv",
            help="The name of the output file"
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
        if arguments.operation == "export-deps":
            GitHub.init(
                ## Workaround as "owner" is currently not working in GHAS Toolkit
                ## The Repo name doesn't matter as we are only using functions that use the owner
                repository=arguments.owner + "/dontcare",
                owner=arguments.owner,
                token=arguments.token
            )
            deps_exporter = DepsExporter(DependencyGraph(), arguments.owner, arguments.csv)
            deps_exporter.run()
        if arguments.operation == "aggregate-licenses":
            logger.info("Aggregating Licenses from %s to %s", arguments.source_csv, arguments.target_csv)
            aggregate_license(arguments.source_csv, arguments.target_csv)


if __name__ == "__main__":
    try:
        cli = CLI()
        cli.run(cli.parse_args())
    except Exception as err:
        logger.error(err)
        exit(1)
