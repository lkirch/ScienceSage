import json
import argparse
from pathlib import Path
from datetime import datetime

# Expanded Golden Dataset with 3 levels per topic
GOLDEN_EXAMPLES = [
    # ---------- SPACE ----------
    {"query": "What is the James Webb Space Telescope used for?",
     "expected_answer": {
         "middle_school": "It looks at space in infrared to learn about stars, planets, and galaxies.",
         "college": "JWST observes the universe in infrared to study early galaxies, star formation, and exoplanet atmospheres.",
         "advanced": "JWST provides high-resolution infrared imaging and spectroscopy, enabling analysis of early galaxy formation, stellar evolution, and detailed exoplanet atmospheric composition."
     },
     "topic": "Space", "source_hint": "NASA Fact Sheets"},
    
    {"query": "What is a supernova?",
     "expected_answer": {
         "middle_school": "A supernova is a star exploding.",
         "college": "A supernova is the explosive death of a star, releasing energy and creating heavy elements.",
         "advanced": "A supernova results from the terminal stage of stellar evolution, either core-collapse of massive stars or thermonuclear runaway in white dwarfs, generating shockwaves and nucleosynthesis of elements beyond iron."
     },
     "topic": "Space", "source_hint": "NASA Supernova Basics"},
    
    # ---------- CLIMATE ----------
    {"query": "What is global warming?",
     "expected_answer": {
         "middle_school": "The Earth is getting hotter because of gases in the air.",
         "college": "Global warming is the long-term rise in Earth's average temperature caused by greenhouse gas emissions.",
         "advanced": "Anthropogenic global warming arises from increased greenhouse gas concentrations, altering radiative forcing, energy balance, and climate feedback mechanisms, impacting global temperature trends and ecosystems."
     },
     "topic": "Climate", "source_hint": "IPCC AR6"},
    
    {"query": "What is the greenhouse effect?",
     "expected_answer": {
         "middle_school": "Some gases trap heat so Earth stays warm.",
         "college": "The greenhouse effect traps infrared radiation using gases like CO₂ and CH₄, warming Earth's surface.",
         "advanced": "The greenhouse effect involves selective absorption and re-emission of infrared radiation by greenhouse gases, modifying Earth's radiative energy balance and driving climate system dynamics."
     },
     "topic": "Climate", "source_hint": "NASA Climate Kids"},
    
    # ---------- AI CONCEPTS ----------
    {"query": "What is reinforcement learning?",
     "expected_answer": {
         "middle_school": "A computer learns by trying things and seeing what works best.",
         "college": "Reinforcement learning is a method where an agent learns to maximize reward by interacting with an environment.",
         "advanced": "Reinforcement learning formalizes decision-making via Markov Decision Processes, with agents optimizing cumulative expected reward through exploration and exploitation policies."
     },
     "topic": "AI Concepts", "source_hint": "Sutton & Barto"},

    {"query": "What is a neural network?",
     "expected_answer": {
         "middle_school": "A neural network is like a brain for a computer.",
         "college": "A neural network is a set of interconnected nodes that transforms inputs to outputs.",
         "advanced": "Neural networks are computational models with layered structures of nonlinear nodes, trained via backpropagation to approximate complex functions over high-dimensional data."
     },
     "topic": "AI Concepts", "source_hint": "Deep Learning Textbook"},
]

def save_dataset(examples, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"golden_dataset_{timestamp}.jsonl"
    latest_path = output_dir / "golden_dataset.jsonl"

    with open(output_path, "w") as f_out:
        for item in examples:
            f_out.write(json.dumps(item) + "\n")

    latest_path.write_text("\n".join(json.dumps(item) for item in examples))
    print(f"✅ Golden dataset written to {output_path}")
    print(f"🔗 Latest alias saved to {latest_path}")

def append_interactively(latest_path):
    print("🔧 Enter new golden examples (Ctrl+C to stop):")
    examples = []
    while True:
        try:
            query = input("Query: ").strip()
            if not query:
                continue
            expected_middle = input("Expected Answer (Middle School): ").strip()
            expected_college = input("Expected Answer (College): ").strip()
            expected_advanced = input("Expected Answer (Advanced): ").strip()
            topic = input("Topic (Space, Climate, AI Concepts): ").strip() or "General"
            source_hint = input("Source Hint: ").strip()
            examples.append({
                "query": query,
                "expected_answer": {
                    "middle_school": expected_middle,
                    "college": expected_college,
                    "advanced": expected_advanced
                },
                "topic": topic,
                "source_hint": source_hint
            })
        except KeyboardInterrupt:
            print("\n🛑 Stopping input.")
            break

    if examples:
        with open(latest_path, "a") as f_out:
            for item in examples:
                f_out.write(json.dumps(item) + "\n")
        print(f"✅ Appended {len(examples)} new examples to {latest_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create or append to a golden dataset with 3 levels for retrieval evaluation.")
    parser.add_argument("--append", action="store_true", help="Append interactively to existing dataset.")
    args = parser.parse_args()

    output_dir = Path("data/eval")
    latest_path = output_dir / "golden_dataset.jsonl"

    if args.append and latest_path.exists():
        append_interactively(latest_path)
    else:
        save_dataset(GOLDEN_EXAMPLES, output_dir)
