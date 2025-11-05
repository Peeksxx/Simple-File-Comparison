import os
import filecmp


def compare_folders(folder1, folder2):
    print(f"\nComparing folders:\n  {folder1}\n  {folder2}\n")

    comparison = filecmp.dircmp(folder1, folder2)

    def report(comp, level=0):
        indent = "  " * level
        print(f"{indent}Checking {comp.left} vs {comp.right}...")

        for fname in comp.common_files:
            f1 = os.path.join(comp.left, fname)
            f2 = os.path.join(comp.right, fname)
            if not filecmp.cmp(f1, f2, shallow=True):
                print(f"{indent}  Possibly different: {fname}")

        if comp.left_only:
            print(f"{indent}  Only in {comp.left}: {comp.left_only}")
        if comp.right_only:
            print(f"{indent}  Only in {comp.right}: {comp.right_only}")

        for subdir, subcomp in comp.subdirs.items():
            report(subcomp, level + 1)

    report(comparison)

    match, mismatch, errors = filecmp.cmpfiles(
        folder1, folder2, comparison.common_files, shallow=True
    )

    all_identical = (
        not comparison.left_only
        and not comparison.right_only
        and not mismatch
        and all(not sub.left_only and not sub.right_only for sub in comparison.subdirs.values())
    )

    if all_identical:
        print("\nThe two folders appear identical (by names, sizes, and timestamps).")
    else:
        print("\nThe two folders differ in structure or metadata.")


if __name__ == "__main__":
    folder1 = input("Enter path to first folder: ").strip('" ')
    folder2 = input("Enter path to second folder: ").strip('" ')

    if not os.path.isdir(folder1) or not os.path.isdir(folder2):
        print("One or both paths are invalid. Please check and try again.")
    else:
        compare_folders(folder1, folder2)
