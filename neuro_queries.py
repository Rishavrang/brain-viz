from neuro_models import Studies, Concept, Coordinate, Study_concept
from database import SessionLocal, engine, Base
from math import sqrt

def get_regions_for_concept(concept_name, db):
    concept = db.query(Concept).filter(Concept.name==concept_name).first()
    if concept is None:
        return {"coordinates":[], "top_studies":[]}
    study_concepts =  db.query(Study_concept).filter(Study_concept.concepts_id==concept.id).order_by(Study_concept.weight.desc()).limit(5).all()
    study_ids = [x.study_id for x in study_concepts]
    coordinate_row =  db.query(Coordinate).filter(Coordinate.study_id.in_(study_ids)).all()
    studies = db.query(Studies).filter(Studies.id.in_(study_ids)).all()
    studyid_to_weight = {c.study_id:c.weight for c in study_concepts}
    studyid_to_name_and_author = {c.id:{"name":c.name, "author":c.author}for c in studies}

    coords ={}
    for c in coordinate_row:
        if c.study_id in coords.keys():
            coords[c.study_id].append(c)
        else:
            coords[c.study_id]=[c]

    final_coords = []

    for key in coords:
        coordx = [c.x for c in coords[key]]
        coordy = [c.y for c in coords[key]]
        coordz = [c.z for c in coords[key]]
        meanx = sum(coordx)/len(coordx)
        meany = sum(coordy)/len(coordy)
        meanz = sum(coordz)/len(coordz)
        coord_distance = [ sqrt((c.x-meanx)**2 + (c.y-meany)**2 + (c.z-meanz)**2) for c in coords[key]]
        min_distance = min(coord_distance)
        min_coordinate = coord_distance.index(min_distance)
        coordinate = (coords[key])[min_coordinate]
        final_coords.append(coordinate)

    

    coordinates = [{"x":c.x, "y":c.y, "z":c.z, "weight":studyid_to_weight[c.study_id], "study_name":studyid_to_name_and_author[c.study_id]["name"], "study_author":studyid_to_name_and_author[c.study_id]["author"]} for c in final_coords]
    concepts =  [{"weight":c.weight, "study_id":c.study_id} for c in study_concepts]
    for y in concepts:
        for z in studies:
            if y["study_id"]==z.id:
                y["name"]=z.name
                y["author"]=z.author
                y["publication"]=z.publication


    return {"coordinates": coordinates, "top_studies": concepts}
