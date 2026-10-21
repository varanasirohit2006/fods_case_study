import json
from pathlib import Path

REPORT = Path(__file__).with_name("zomato_2.Report") / "report.json"
ENTITY = "cleaned_zomato_data"


def column(field):
    return {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": field}, "Name": f"{ENTITY}.{field}"}


def measure(field):
    return {"Measure": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": field}, "Name": f"{ENTITY}.{field}"}


def visual(name, kind, projections, selects, title, x, y=105, width=400, height=595):
    # Keep the report stable in Power BI Desktop: legends/series can exceed a
    # visual's column limit when combined with multiple measures. The same
    # comparisons remain interactive through the page slicers and cross-filtering.
    projections = {key: value for key, value in projections.items() if key != "Series"}
    cfg = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 1, "width": width, "height": height, "tabOrder": 1}}],
        "singleVisual": {
            "visualType": kind,
            "projections": projections,
            "prototypeQuery": {"Version": 2, "From": [{"Name": "c", "Entity": ENTITY, "Type": 0}], "Select": selects},
            "drillFilterOtherVisuals": True,
            "vcObjects": {"title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": repr(title)}}}}}]},
        },
    }
    return {"x": x, "y": y, "z": 1, "width": width, "height": height, "config": json.dumps(cfg), "filters": "[]"}


def slicer(name, field, title, x):
    cfg = {
        "name": name,
        "layouts": [{"id": 0, "position": {"x": x, "y": 15, "z": 10, "width": 300, "height": 75, "tabOrder": 10}}],
        "singleVisual": {
            "visualType": "slicer",
            "projections": {"Values": [{"queryRef": f"{ENTITY}.{field}", "active": True}]},
            "prototypeQuery": {"Version": 2, "From": [{"Name": "c", "Entity": ENTITY, "Type": 0}], "Select": [column(field)]},
            "drillFilterOtherVisuals": True,
            "vcObjects": {"title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": repr(title)}}}}}]},
            "objects": {"data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Basic'"}}}}}], "general": [{"properties": {"orientation": {"expr": {"Literal": {"Value": "1D"}}}}}]},
        },
    }
    return {"x": x, "y": 15, "z": 10, "width": 300, "height": 75, "config": json.dumps(cfg), "filters": "[]"}


def build_page(page_index, name, visuals, filters):
    containers = visuals + [slicer(f"p{page_index}_slicer_{i}", field, title, 20 + i * 310) for i, (field, title) in enumerate(filters)]
    return {"name": f"ReportSection{page_index}", "displayName": name, "filters": "[]", "ordinal": page_index - 1, "visualContainers": containers, "config": json.dumps({"name": f"ReportSection{page_index}"}), "displayOption": 1, "width": 1280, "height": 720}


def main():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    pages = [
        build_page(1, "1. Executive Command Center", [
            visual("p1_orders", "lineChart", {"Category": [{"queryRef": f"{ENTITY}.Order_Date", "active": True}], "Y": [{"queryRef": f"{ENTITY}.Total Orders"}]}, [column("Order_Date"), measure("Total Orders")], "Daily Order Demand Trend", 20, width=600),
            visual("p1_city", "donutChart", {"Category": [{"queryRef": f"{ENTITY}.City", "active": True}], "Y": [{"queryRef": f"{ENTITY}.Total Orders"}]}, [column("City"), measure("Total Orders")], "Order Mix by City Tier", 640, width=600),
            visual("p1_type", "clusteredColumnChart", {"Category": [{"queryRef": f"{ENTITY}.Type_of_order", "active": True}], "Y": [{"queryRef": f"{ENTITY}.Avg Delivery Time (min)"}], "Series": [{"queryRef": f"{ENTITY}.Festival", "active": True}]}, [column("Type_of_order"), measure("Avg Delivery Time (min)"), column("Festival")], "Order Type and Festival Performance", 20, y=410, width=600, height=270),
        ], [("City", "Filter: City Tier"), ("Road_traffic_density", "Filter: Traffic"), ("Festival", "Filter: Festival"), ("Order_Date", "Filter: Order Date")]),
        build_page(2, "2. Bottleneck Explorer", [
            visual("p2_weather", "clusteredBarChart", {"Category": [{"queryRef": f"{ENTITY}.Weather_conditions", "active": True}], "Y": [{"queryRef": f"{ENTITY}.Avg Delivery Time (min)"}]}, [column("Weather_conditions"), measure("Avg Delivery Time (min)")], "Average Delivery Time by Weather", 20),
            visual("p2_heatmap", "matrix", {"Rows": [{"queryRef": f"{ENTITY}.Weather_conditions", "active": True}], "Columns": [{"queryRef": f"{ENTITY}.Road_traffic_density", "active": True}], "Values": [{"queryRef": f"{ENTITY}.Avg Delivery Time (min)"}]}, [column("Weather_conditions"), column("Road_traffic_density"), measure("Avg Delivery Time (min)")], "Weather × Traffic Bottleneck Matrix", 440),
            visual("p2_combo", "lineClusteredColumnComboChart", {"Category": [{"queryRef": f"{ENTITY}.Road_traffic_density", "active": True}], "Y": [{"queryRef": f"{ENTITY}.Total Orders"}], "Y2": [{"queryRef": f"{ENTITY}.Avg Delivery Time (min)"}]}, [column("Road_traffic_density"), measure("Total Orders"), measure("Avg Delivery Time (min)")], "Traffic Volume vs Delivery Time", 860),
        ], [("City", "Filter: City Tier"), ("Weather_conditions", "Filter: Weather"), ("Road_traffic_density", "Filter: Traffic"), ("Festival", "Filter: Festival")]),
        build_page(3, "3. Fleet Performance Lab", [
            visual("p3_fleet", "donutChart", {"Category": [{"queryRef": f"{ENTITY}.Type_of_vehicle", "active": True}], "Y": [{"queryRef": f"{ENTITY}.Total Orders"}]}, [column("Type_of_vehicle"), measure("Total Orders")], "Fleet Mix by Vehicle Type", 20),
            visual("p3_condition", "clusteredColumnChart", {"Category": [{"queryRef": f"{ENTITY}.Vehicle_condition", "active": True}], "Y": [{"queryRef": f"{ENTITY}.Avg Delivery Time (min)"}], "Series": [{"queryRef": f"{ENTITY}.Type_of_vehicle", "active": True}]}, [column("Vehicle_condition"), measure("Avg Delivery Time (min)"), column("Type_of_vehicle")], "Vehicle Condition Impact by Fleet Type", 440),
            visual("p3_rating", "clusteredBarChart", {"Category": [{"queryRef": f"{ENTITY}.Delivery_person_Ratings", "active": True}], "Y": [{"queryRef": f"{ENTITY}.Avg Delivery Time (min)"}]}, [column("Delivery_person_Ratings"), measure("Avg Delivery Time (min)")], "Partner Rating vs Delivery Speed", 860),
        ], [("Type_of_vehicle", "Filter: Vehicle Type"), ("Vehicle_condition", "Filter: Vehicle Condition"), ("City", "Filter: City Tier"), ("Road_traffic_density", "Filter: Traffic")]),
        build_page(4, "4. Logistics & Demand Simulator", [
            visual("p4_scatter", "scatterChart", {"X": [{"queryRef": f"{ENTITY}.delivery_distance_km", "active": True}], "Y": [{"queryRef": f"{ENTITY}.Time_taken_min", "active": True}], "Details": [{"queryRef": f"{ENTITY}.City", "active": True}]}, [column("delivery_distance_km"), column("Time_taken_min"), column("City")], "Distance vs Delivery Duration", 20),
            visual("p4_hour", "lineClusteredColumnComboChart", {"Category": [{"queryRef": f"{ENTITY}.hour_of_day", "active": True}], "Y": [{"queryRef": f"{ENTITY}.Total Orders"}], "Y2": [{"queryRef": f"{ENTITY}.Avg Delivery Time (min)"}]}, [column("hour_of_day"), measure("Total Orders"), measure("Avg Delivery Time (min)")], "Hourly Demand and Delivery Time", 440),
            visual("p4_prep", "clusteredBarChart", {"Category": [{"queryRef": f"{ENTITY}.Type_of_order", "active": True}], "Y": [{"queryRef": f"{ENTITY}.Avg Prep Time (min)"}, {"queryRef": f"{ENTITY}.Avg Delivery Time (min)"}], "Series": [{"queryRef": f"{ENTITY}.City", "active": True}]}, [column("Type_of_order"), measure("Avg Prep Time (min)"), measure("Avg Delivery Time (min)"), column("City")], "Preparation vs Delivery Time", 860),
        ], [("City", "Filter: City Tier"), ("Type_of_order", "Filter: Order Type"), ("multiple_deliveries", "Filter: Batch Size"), ("Road_traffic_density", "Filter: Traffic")]),
        build_page(5, "5. Partner & Decision Studio", [
            visual("p5_day", "lineChart", {"Category": [{"queryRef": f"{ENTITY}.day_of_week", "active": True}], "Y": [{"queryRef": f"{ENTITY}.Avg Delivery Time (min)"}], "Series": [{"queryRef": f"{ENTITY}.City", "active": True}]}, [column("day_of_week"), measure("Avg Delivery Time (min)"), column("City")], "Delivery Time by Day and City Tier", 20),
            visual("p5_batch", "clusteredColumnChart", {"Category": [{"queryRef": f"{ENTITY}.multiple_deliveries", "active": True}], "Y": [{"queryRef": f"{ENTITY}.Avg Delivery Time (min)"}], "Series": [{"queryRef": f"{ENTITY}.Festival", "active": True}]}, [column("multiple_deliveries"), measure("Avg Delivery Time (min)"), column("Festival")], "Batching Penalty: Festival vs Non-Festival", 440),
            visual("p5_age", "scatterChart", {"X": [{"queryRef": f"{ENTITY}.Delivery_person_Age", "active": True}], "Y": [{"queryRef": f"{ENTITY}.Time_taken_min", "active": True}], "Details": [{"queryRef": f"{ENTITY}.Delivery_person_ID", "active": True}]}, [column("Delivery_person_Age"), column("Time_taken_min"), column("Delivery_person_ID")], "Partner Age vs Delivery Duration", 860),
        ], [("City", "Filter: City Tier"), ("day_of_week", "Filter: Day of Week"), ("Festival", "Filter: Festival"), ("Delivery_person_Ratings", "Filter: Partner Rating")]),
    ]
    report["sections"] = pages
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Updated five distinct interactive report pages.")


if __name__ == "__main__":
    main()
