from analyzer import analyze_email, analyze_job_description, analyze_review
from storage import save_result


def read_multiline_text() -> str:
    print("\nPaste the text below.")
    print("Type END on a new line when finished.\n")

    lines = []

    while True:
        line = input()

        if line.strip().upper() == "END":
            break

        lines.append(line)

    return "\n".join(lines).strip()


def main():
    print("AI Text Analyzer")

    while True:
        print("1. Analyze job description")
        print("2. Analyze email")
        print("3. Analyze product review")
        print("4. Exit")

        choice = input("\nChoice: ").strip()

        if choice == "4":
            print("Goodbye.")
            break

        if choice not in {"1", "2", "3"}:
            print("Invalid option.")
            continue

        text = read_multiline_text()

        if not text:
            print("No text was entered.")
            continue

        try:
            if choice == "1":
                result = analyze_job_description(text)
            elif choice == "2":
                result = analyze_email(text)
            else:
                result = analyze_review(text)

            print("\nAnalysis:")
            print(result.model_dump_json(indent=2))

            if choice == "1":
                analysis_type = "job"
            elif choice == "2":
                analysis_type = "email"
            else:
                analysis_type = "review"

            file_path = save_result(result, analysis_type)

            print(f"\nSaved to: {file_path}")

        except Exception as error:
            print("Something went wrong:", error)


if __name__ == "__main__":
    main()