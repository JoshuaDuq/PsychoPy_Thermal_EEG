import os
import glob
import pandas as pd
import argparse


def combine_trial_summaries(participant_id: str, runs: int = 5, data_dir: str = "data") -> str:
    """Combine per-run TrialSummary CSVs into a single file.

    Parameters
    ----------
    participant_id : str
        ID of the participant (folder inside ``data``).
    runs : int, optional
        Number of runs to combine, by default 5.
    data_dir : str, optional
        Base ``data`` directory path, by default ``"data"``.

    Returns
    -------
    str
        Path to the combined CSV written to disk.
    """
    participant_dir = os.path.join(data_dir, participant_id)
    if not os.path.isdir(participant_dir):
        raise FileNotFoundError(f"Participant directory not found: {participant_dir}")

    frames = []
    for run in range(1, runs + 1):
        pattern = os.path.join(
            participant_dir,
            f"{participant_id}_ThermalPainEEGFMRI_run{run}_*_TrialSummary.csv",
        )
        matches = glob.glob(pattern)
        if not matches:
            raise FileNotFoundError(f"No TrialSummary CSV found for run {run}: {pattern}")
        # Use the first match (should only be one per run)
        csv_path = matches[0]
        df = pd.read_csv(csv_path)
        df = df.sort_values("trial_number")
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    combined["trial_number"] = range(1, len(combined) + 1)

    out_path = os.path.join(
        participant_dir,
        f"{participant_id}_ThermalPainEEGFMRI_ALL_TrialSummary.csv",
    )
    combined.to_csv(out_path, index=False)
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine per-run TrialSummary CSV files.")
    parser.add_argument("participant_id", help="Participant ID (folder name inside data)")
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Base data directory containing participant folders (default: data)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of runs to combine (default: 5)",
    )
    args = parser.parse_args()
    out_csv = combine_trial_summaries(args.participant_id, args.runs, args.data_dir)
    print(f"Combined trial summary saved to {out_csv}")
