def animal_recommendation(disease):
    mapping = {
        "lumpy": {
            "vitamins": ["Vitamin B12"],
            "diet": ["Milk", "Green Fodder", "Mineral Mix"]
        },
        "fungal_infections": {
            "vitamins": ["Vitamin A"],
            "diet": ["Eggs", "Fish Oil"]
        },
        "ringworm": {
            "vitamins": ["Vitamin D"],
            "diet": ["Fish", "Eggs"]
        }
    }
    return mapping.get(disease, {"vitamins": [], "diet": []})


def human_recommendation(disease):
    mapping = {
        "Melanoma": {
            "vitamins": ["Vitamin D"],
            "diet": ["Fruits", "Vegetables"]
        },
        "Vascular Lesion": {
            "vitamins": ["Vitamin C"],
            "diet": ["Citrus Fruits"]
        }
    }
    return mapping.get(disease, {"vitamins": [], "diet": []})
