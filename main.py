from dotenv import load_dotenv
from ai_module.pipeline import process_prescription

load_dotenv()


def main():
    # Change this to any image path from your dataset
    test_image = "/mnt/g/AI/My Projects/data/images/test/msg1484047343-32899_jpg.rf.c635178e56877adaf9a84140de53c8dd.jpg"
    print("Running MediScan AI pipeline...")
    result = process_prescription(test_image)

    if result["success"]:
        print("\nExtracted Text:")
        print(result["raw_text"])
        print("\nMedications Found:")
        for med in result["medications"]:
            print(f"  - {med['name']} | {med['dosage']} | {med['frequency']} | {med['duration']}")
    else:
        print(f"\nError: {result['error']}")


if __name__ == "__main__":
    main()