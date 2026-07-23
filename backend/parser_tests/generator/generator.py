import argparse
import json
import os
import shutil
import sys

# Add backend dir to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from parser_tests.generator.metadata.ground_truth import (
    generate_expected_json, generate_metadata_json, generate_notes_md)
from parser_tests.generator.profiles.builder import ResumeProfileBuilder
from parser_tests.generator.templates.markdown import generate_markdown
from parser_tests.generator.templates.pdf import generate_pdf


def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def generate_resume_bundle(
    builder: ResumeProfileBuilder, output_dir: str, index: int, **kwargs
):
    # Generate structured profile
    profile = builder.generate_profile(**kwargs)

    # Generate naming convention for folder
    ind = profile["metadata"]["industry"].replace(" ", "_").replace("/", "_").lower()
    exp = (
        profile["metadata"]["experience_level"]
        .replace(" ", "_")
        .replace("-", "_")
        .lower()
    )
    folder_name = f"{ind}_{exp}_{index:03d}"

    bundle_dir = os.path.join(output_dir, folder_name)
    ensure_dir(bundle_dir)

    # 1. JSON Ground Truth
    expected = generate_expected_json(profile)
    with open(os.path.join(bundle_dir, "expected.json"), "w", encoding="utf-8") as f:
        json.dump(expected, f, indent=2)

    # 2. Metadata JSON
    meta = generate_metadata_json(profile)
    with open(os.path.join(bundle_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # 3. Notes MD
    notes = generate_notes_md(profile)
    with open(os.path.join(bundle_dir, "notes.md"), "w", encoding="utf-8") as f:
        f.write(notes)

    # 4. Markdown Format
    md_text = generate_markdown(profile)
    with open(os.path.join(bundle_dir, "resume.md"), "w", encoding="utf-8") as f:
        f.write(md_text)

    # 5. PDF Format
    pdf_path = os.path.join(bundle_dir, "resume.pdf")
    generate_pdf(profile, pdf_path)

    # Copy expected.json and resume.pdf to the main test folders to easily plug into the existing benchmark suite
    main_resumes = os.path.abspath(
        os.path.join(output_dir, "../../datasets/sample_resumes")
    )
    main_expected = os.path.abspath(
        os.path.join(output_dir, "../../datasets/expected_outputs")
    )

    ensure_dir(main_resumes)
    ensure_dir(main_expected)

    shutil.copy(pdf_path, os.path.join(main_resumes, f"{folder_name}.pdf"))
    with open(
        os.path.join(main_expected, f"{folder_name}.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(expected, f, indent=2)

    return folder_name


def distribute_experience_levels(total_count: int):
    # Try to balance across No Experience, Junior, Mid, Senior, etc.
    dist = []
    levels = ["No experience", "0-2 years", "2-5 years", "5-10 years", "10-20 years"]
    for i in range(total_count):
        dist.append(levels[i % len(levels)])
    return dist


def main():
    parser = argparse.ArgumentParser(description="Benchmark Resume Dataset Generator")
    parser.add_argument(
        "--count", type=int, default=50, help="Number of resumes to generate"
    )
    parser.add_argument("--industry", type=str, help="Force a specific industry")
    parser.add_argument(
        "--experience", type=str, help="Force a specific experience level"
    )
    parser.add_argument("--country", type=str, help="Force a specific country format")
    parser.add_argument("--difficulty", type=str, help="Force difficulty")
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility"
    )

    args = parser.parse_args()

    print(f"Initializing Dataset Generator (Seed: {args.seed})...")
    builder = ResumeProfileBuilder(seed=args.seed)

    output_dir = os.path.join(os.path.dirname(__file__), "output")

    # If no specific experience level requested, distribute them evenly
    exp_distribution = (
        distribute_experience_levels(args.count)
        if not args.experience
        else [args.experience] * args.count
    )

    print(f"Generating {args.count} realistic resumes...")

    for i in range(args.count):
        kwargs = {}
        if args.industry:
            kwargs["industry"] = args.industry
        if args.country:
            kwargs["country"] = args.country

        # Use distributed experience if not explicitly provided
        kwargs["experience"] = exp_distribution[i]

        folder = generate_resume_bundle(builder, output_dir, i + 1, **kwargs)
        print(f"[{i+1}/{args.count}] Generated {folder}")

    print("\nDataset generation complete.")
    print(f"Raw bundles stored in: {output_dir}")
    print(
        "PDFs and Expected JSONs have been automatically linked to the benchmark suite directories."
    )


if __name__ == "__main__":
    main()
