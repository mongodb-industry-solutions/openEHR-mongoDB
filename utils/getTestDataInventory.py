import os

def analyze_compositions(base_dir):
    compositions = {}

    # Traverse the folder structure
    for root, dirs, files in os.walk(base_dir):
        for folder in dirs:
            # Each folder inside compositionLevel represents a composition
            composition_path = os.path.join(root, folder)
            if root.endswith('compositionLevel'):  # Ensure we're in compositionLevel
                if folder not in compositions:
                    compositions[folder] = {
                        'AQL': [],
                        'Archetypes': [],
                        'Templates': {
                            'opt': [],
                            'json': [],
                            'webtemplate': []
                        },
                        'Compositions': 0
                    }

                # Dive into the folder to count and categorize files
                for subroot, subdirs, subfiles in os.walk(composition_path):
                    for subfile in subfiles:
                        if subfile.endswith('.aql'):
                            compositions[folder]['AQL'].append(subfile)
                        elif subfile.endswith('.opt'):
                            compositions[folder]['Templates']['opt'].append(subfile)
                        elif subfile.endswith('.json'):
                            compositions[folder]['Templates']['json'].append(subfile)
                        elif subfile.endswith('.webtemplate'):
                            compositions[folder]['Templates']['webtemplate'].append(subfile)
                        elif subfile.endswith('.xml'):  # Example for compositions as instances
                            compositions[folder]['Compositions'] += 1
                        elif subfile.startswith('archetype'):
                            compositions[folder]['Archetypes'].append(subfile)

    return compositions

def main():
    # Adjust the base_dir based on your actual path structure
    base_dir = os.path.join(os.path.dirname(__file__), '../testData/compositionLevel')
    if not os.path.exists(base_dir):
        print(f"Error: Base directory {base_dir} does not exist.")
        return

    results = analyze_compositions(base_dir)

    if not results:
        print("No compositions found. Check the folder structure and ensure it matches expectations.")
        return

    # Print results in a structured way
    for comp, data in results.items():
        print(f"Composition: {comp}")
        print(f"  AQLs: {', '.join(data['AQL']) if data['AQL'] else 'None'}")
        print(f"  Archetypes: {', '.join(data['Archetypes']) if data['Archetypes'] else 'None'}")
        print("  Templates:")
        for key, templates in data['Templates'].items():
            print(f"    {key}: {', '.join(templates) if templates else 'None'}")
        print(f"  Number of Compositions: {data['Compositions']}")
        print("\n")

if __name__ == "__main__":
    main()