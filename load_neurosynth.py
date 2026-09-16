from nimare.extract import fetch_neurosynth
from database import SessionLocal, engine, Base
from neuro_models import Studies, Coordinate

Base.metadata.create_all(bind=engine)

files = fetch_neurosynth(
    data_dir="neurosynth_data",
    version="7",
    source="abstract",
    vocab="terms",
)

studyset = files[0]
coords_df = studyset.coordinates
studies_list = studyset.studies

db = SessionLocal()

unique_study_ids =  coords_df["study_id"].unique()
study_records = [{"id": study.id, "name":study.name, "author":study.authors,"publication":study.publication, "publish_date":study.year} for study in studies_list]
db.bulk_insert_mappings(Studies, study_records)
db.commit()
print(f"Inserted {len(study_records)} studies")

coord_records = [{"x":row.x, "y":row.y, "z":row.z, "study_id":row.study_id} for row in coords_df.itertuples()]
db.bulk_insert_mappings(Coordinate, coord_records)
db.commit()
print(f"Inserted {len(coord_records)}coordinates")