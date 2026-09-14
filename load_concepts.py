import numpy as np
from nimare.extract import fetch_neurosynth
from database import SessionLocal, engine, Base
from neuro_models import Concept, Study_concept

Base.metadata.create_all(bind=engine)

files = fetch_neurosynth(
    data_dir="neurosynth_data",
    version="7",
    source="abstract",
    vocab="terms",
)
studyset = files[0]
annotations_df = studyset.annotations_df

term_cols =  [c for c in annotations_df.columns if c.startswith("terms_abstract_tfidf__")]
values = annotations_df[term_cols].values
study_ids =  annotations_df["study_id"].values

threshold = 0.001
rows, cols = np.nonzero(values>threshold)

concept_names =  [term_cols[c].replace("terms_abstract_tfidf__","") for c in cols]
weights =  values[rows, cols]
matched_study_ids = study_ids[rows]

print(f"Found {len(concept_names)} meaningful study-concept pairs")

db=SessionLocal()

unique_concepts = sorted(set(concept_names))
concept_records = [{"name":name} for name in unique_concepts]
db.bulk_insert_mappings(Concept, concept_records)
db.commit()
print(f"Inserted {len(concept_records)} concepts") 

concept_name_to_id = {c.name: c.id for c in db.query(Concept).all()}

study_concept_records = [
    {
        "study_id": str(matched_study_ids[i]),
        "concepts_id": concept_name_to_id[concept_names[i]],
        "weight": float(weights[i])
    }
    for i in range(len(concept_names))
]
db.bulk_insert_mappings(Study_concept, study_concept_records)
db.commit()
print(f"Inserted {len(study_concept_records)} study-concept links")