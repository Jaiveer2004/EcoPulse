import argparse

from pathlib import Path

from ecopulse.simulation.sensor_generator import (
    generate_batch,
    save_events,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic EcoPulse sensor events"
    )
    
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of time intervals to generate",
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for reproducibility",
    )
    
    args = parser.parse_args()
    
    events = generate_batch(
        count=args.count,
        seed=args.seed,
    )
    
    output_dir = PROJECT_ROOT / "data/synthetic/sensor_events"
    
    output_path = save_events(
        events=events,
        output_dir=output_dir,
    )
    
    print("\nEcoPulse Synthetic Sensor Generator")
    print("=" * 40)
    print(f"Intervals generated: {args.count}")
    print("Sensors: 2")
    print(f"Total events: {len(events)}")
    print("Source type: synthetic")
    print(f"Output file: {output_path}")


if __name__ == "__main__":
    main()
