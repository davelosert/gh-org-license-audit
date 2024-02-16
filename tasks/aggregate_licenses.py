import csv

def aggregate_license(source_csv, target_csv):
    """Aggregates all licenses previously found by the export-deps command"""
    

    with open(source_csv, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        licenses = {}
        for row in reader:
            license = row[2]
            if license in licenses:
                licenses[license] += 1
            else:
                licenses[license] = 0


        with open(target_csv, "w", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["License", "Count"])
            
            
            licenses = dict(sorted(licenses.items(), key=lambda item: item[1], reverse=True))
            for license, count in licenses.items():
                writer.writerow([license, str(count)])
