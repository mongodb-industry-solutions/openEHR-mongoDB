import os

def analyze_compositions(base_dir):
    compositions = {}

    # Traverse the folder structure
    for root, dirs, files in os.walk(base_dir):
        for folder in dirs:
            # Each folder inside compositionLevel represents a composition
            composition_path = os.path.join(root, folder)
            if root.endswith('compositionLevel'):
                if folder not in compositions:
                    compositions[folder] = {
                        'AQL': [],
                        'Archetypes': [],
                        'Templates': {
                            'opt': [],
                            'json': [],
                            'webtemplate': 'No'
                        },
                        'Composition Instances': 0,
                        'Sufficient data for querying': ''
                    }

                # Dive into the folder to count and categorize files
                for subroot, subdirs, subfiles in os.walk(composition_path):
                    if subroot.endswith('AQLS'):  # Add directory names under AQLS
                        compositions[folder]['AQL'].extend(subdirs)
                    for subfile in subfiles:
                        if subroot.endswith('Archetypes'):  # Archetypes are .adl files
                            if subfile.endswith('.adl'):
                                compositions[folder]['Archetypes'].append(os.path.splitext(subfile)[0])
                        elif subroot.endswith('Templates'):  # Templates categorize by extension
                            if subfile.endswith('.opt'):
                                compositions[folder]['Templates']['opt'].append(subfile)
                            elif subfile.endswith('.json'):
                                compositions[folder]['Templates']['json'].append(subfile)
                        elif subroot.endswith('Compositions'):  # Count instances in Compositions
                            compositions[folder]['Composition Instances'] += 1

                    # Check if WebTemplate folder is present
                    if 'WebTemplates' in subdirs:
                        compositions[folder]['Templates']['webtemplate'] = 'Yes'

                # Sort the results alphabetically
                compositions[folder]['AQL'].sort()
                compositions[folder]['Archetypes'].sort()
                compositions[folder]['Templates']['opt'].sort()
                compositions[folder]['Templates']['json'].sort()

                # Determine if sufficient data for querying exists
                if compositions[folder]['AQL'] and compositions[folder]['Composition Instances'] > 0:
                    compositions[folder]['Sufficient data for querying'] = 'Yes'
                elif not compositions[folder]['AQL']:
                    compositions[folder]['Sufficient data for querying'] = 'No, we need AQLs'
                elif compositions[folder]['Composition Instances'] == 0:
                    compositions[folder]['Sufficient data for querying'] = 'No, we need Composition instances'

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
            print(f"    {key}: {templates if isinstance(templates, str) else ', '.join(templates) if templates else 'None'}")
        print(f"  Composition Instances: {data['Composition Instances']}")
        print(f"  Sufficient data for querying: {data['Sufficient data for querying']}")
        print("\n")

if __name__ == "__main__":
    main()