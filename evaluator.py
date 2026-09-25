import requests
import csv

scenarios = [ 
    "The weather is nice today",
    "I'm making a sandwich for lunch"
]
results=[]
for s in scenarios:
    response = requests.post("http://127.0.0.1:8000/new-conversation", json={"name" : "testing"})
    conv_id = response.json()["id"]
    scenario_dict={}
    try :
        response = requests.post("http://127.0.0.1:8000/chat", json={"message":s, "conversation_id":conv_id})
        reply = response.json()
        scenario_dict["scenario"] = s
        scenario_dict["coordinates"] = reply["coordinates"]
        scenario_dict["concepts"] = reply["detected_concepts"]
        scenario_dict["num_coordinates"] = len(reply["coordinates"])
        scenario_dict["reply"] = reply["reply"]
    except:
        scenario_dict["error"] = "true"
        scenario_dict["scenario"] =s

    results.append(scenario_dict)


print(results)