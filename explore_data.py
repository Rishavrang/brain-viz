from nimare.extract import fetch_neurosynth

files = fetch_neurosynth(
    data_dir="neurosynth_data",
    version="7",
    source="abstract",
    vocab="terms",
)

studyset = files[0]
print(studyset)
print(studyset.coordinates.head())