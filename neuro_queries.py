from neuro_models import Studies, Concept, Coordinate, Study_concept
from database import SessionLocal, engine, Base

def get_regions_for_concept(concept_name, db):
    concept = db.query(Concept).filter(Concept.name==concept_name).first()
    if concept is None:
        return {"coordinates":[], "top_studies":[]}
    study_concepts =  db.query(Study_concept).filter(Study_concept.concepts_id==concept.id).order_by(Study_concept.weight.desc()).limit(5).all()
    study_ids = [x.study_id for x in study_concepts]
    coordinate_row =  db.query(Coordinate).filter(Coordinate.study_id.in_(study_ids)).all()
    studies = db.query(Studies).filter(Studies.id.in_(study_ids)).all()

    coordinates = [{"x":c.x, "y":c.y, "z":c.z} for c in coordinate_row]
    concepts =  [{"weight":c.weight, "study_id":c.study_id} for c in study_concepts]
    for y in concepts:
        for z in studies:
            if y["study_id"]==z.id:
                y["name"]=z.name
                y["author"]=z.author
                y["publication"]=z.publication


    return {"coordinates": coordinates, "top_studies": concepts}
