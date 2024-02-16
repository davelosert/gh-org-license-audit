import logging
import csv
import urllib

class DepsExporter:
    def __init__(self, dependency_graph, organization):
        self.dependency_graph = dependency_graph
        self.organization = organization

    def run(self, target_csv):
        """Writes all found dependencies with a count to a CSV File"""
        logger = logging.getLogger(__name__)

        dependencies = {}

        try:
            org_dependencies = self.dependency_graph.getOrganizationDependencies()
        except Exception as err:
            if str(err) == 'Authentication Issue':
                logger.error('Authentication Issue. Please ensure you GitHub Token is scoped ot the organization %s and has the required permissions "repo:read"', self.organization)
            else:
                logger.error(err)
            exit(1)

        logger.info("Found %s repositories. Extracting SBOMs now. This can take a while...", len(org_dependencies))

        for _, deps in org_dependencies.items():
            for dep in deps:
                if dep in dependencies:
                    dependencies[dep] += 1
                else:
                    dependencies[dep] = 1

        with open(target_csv, "w", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Dependency", "Version", "Licenses", "Count"])

            for dep, count in dependencies.items():
                writer.writerow([urllib.parse.unquote(dep.fullname), dep.version, dep.license or "", str(count)])
