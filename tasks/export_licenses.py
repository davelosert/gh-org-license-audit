import logging
import csv
import urllib

class DepsExporter:
    def __init__(self, dependency_graph, organization, csv_target):
        self.dependency_graph = dependency_graph
        self.organization = organization
        self.csv_target = csv_target

    def run(self):
        """Writes all found dependencies with a count to a CSV File"""
        logger = logging.getLogger(__name__)

        logger.info("Exporting Dependencies from organization %s to %s", self.organization, self.csv_target)
        logger.info("This might take a while...")

        try:
            org_dependencies = self.dependency_graph.getOrganizationDependencies()
        except Exception as err:
            if str(err) == 'Authentication Issue':
                logger.error('Authentication Issue. Please ensure you GitHub Token is scoped ot the organization %s and has the required permissions "repo:read"', self.organization)
            else:
                logger.error(err)
            exit(1)

        dependencies = {}
        for repo, deps in org_dependencies.items():
            for dep in deps:
                # Skip if the dependency is a reference to the repository itself
                # logger.log("Repo: %s, dep.name: %s", repo, dep)
                if dep.fullname == f"{repo.owner}/{repo.repo}":
                    continue
                
                if dep in dependencies:
                    dependencies[dep] += 1
                else:
                    dependencies[dep] = 1

        dependencies = dict(sorted(dependencies.items(), key=lambda item: item[1], reverse=True))

        with open(self.csv_target, "w", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Dependency", "Version", "Licenses", "Count"])

            for dep, count in dependencies.items():
                writer.writerow([urllib.parse.unquote(dep.fullname), dep.version, dep.license or "UNKNOWN", str(count)])
