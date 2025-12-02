from services.google_sheets import read_sheet, append_row
import datetime

def run_gti_loop():
    pred = read_sheet("genie_predictions")

    if len(pred) < 3:
        return "Not enough prediction data"

    deviations = []
    for row in pred[-10:]:
        if row[10]:  # Actual_Price
            try:
                p = float(row[4])
                a = float(row[10])
                dev = abs(a - p) / p * 100
                deviations.append(dev)
            except:
                pass

    if len(deviations) == 0:
        return "No deviation data"

    avg_dev = sum(deviations) / len(deviations)
    gti_score = max(0, 100 - avg_dev)

    row = [
        f"GTI-{datetime.datetime.now().timestamp()}",
        datetime.datetime.now().isoformat(),
        "1h",
        len(deviations),
        round(avg_dev, 3),
        round(gti_score, 2),
        "simple_gti",
        "auto",
        "NEUTRAL",
        "",
    ]
    append_row("genie_gti_log", row)
    return "GTI updated"

