import json
import re


def solution(jsonData):
    jsonData = json.loads(jsonData)
    keywords_to_ignore = ["yoga", "dance", "art"]
    final_list = []
    for data in jsonData:
        # Preprocess description: remove punctuation and convert to lowercase
        description = re.sub(r"[^\w\s]", "", data["description"].lower())
        words = description.split()
        print("Description:", description)
        print("Words:", words)
        if ("studio" in words or "1bedroom" in words) and any(
            keyword in words for keyword in keywords_to_ignore
        ):
            index = (
                words.index("studio") if "studio" in words else words.index("1bedroom")
            )
            print("Index:", index)
            if index > 0 and words[index - 1] in keywords_to_ignore:
                continue
        else:
            final_list.append(data["num_bedrooms"])
    return final_list


jsonData = '[{"id": "1", "agent": "Radulf Katlego", "unit": "#3", "description" : "This luxurious studio apartment is in the heart of downtown.", "num_bedrooms": 1},{"id": "2", "agent": "Kelemen Konrad", "unit": "#36", "description": "We have a 1-bedroom available on the third floor.", "num_bedrooms": 1},{"id": "3", "agent": "Ton Jett", "unit": "#12", "description": "Beautiful 1-bedroom apartment with nearby yoga studio.", "num_bedrooms": 1},{"id": "4", "agent": "Fishel Salman", "unit": "#13", "description": "Beautiful studio with a nearby art studio.", "num_bedrooms": 1}]'

print(solution(jsonData))
