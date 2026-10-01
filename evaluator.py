import requests
import csv

scenarios = [ 
    "Walking through a jungle, seeing a snake, feeling afraid",
    "Trying to remember where you parked your car in a large garage",
    "Solving a difficult math problem under time pressure",
    "Feeling nostalgic looking through old childhood photos",
    "Hearing footsteps behind you at night and feeling anxious",
    "Studying for a big exam while feeling stressed and trying to focus",
    "Meeting someone new and trying to remember their name while feeling socially anxious",
    "Making a risky financial decision while feeling excited and uncertain",
    "Navigating a new city while feeling both curious and a little lost",
    "I had a weird day today",
    "Something happened and I don't know how I feel about it",
    "Thinking about stuff"
]

results = []
for s in scenarios:
    response = requests.post("http://127.0.0.1:8000/new-conversation", json={"name": "testing"})
    conv_id = response.json()["id"]
    scenario_dict = {}
    try:
        response = requests.post("http://127.0.0.1:8000/chat", json={"message": s, "conversation_id": conv_id})
        reply = response.json()
        scenario_dict["scenario"] = s
        scenario_dict["coordinates"] = reply["coordinates"]
        scenario_dict["concepts"] = reply["detected_concepts"]
        scenario_dict["num_coordinates"] = len(reply["coordinates"])
    except:
        scenario_dict["error"] = "true"
        scenario_dict["scenario"] = s

    results.append(scenario_dict)

with open("evaluation_results_batch1.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["scenario", "concepts", "num_coordinates", "error"], extrasaction="ignore")
    writer.writeheader()
    for row in results:
        writer.writerow(row)

print(results)