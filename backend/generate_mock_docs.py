"""
Mock Medical Document Generator — Creates realistic Indian medical documents as images.
Uses Pillow to generate prescription, bill, and diagnostic report images.
"""
import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_documents")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _get_font(size=16, bold=False):
    """Get a font, falling back to default if custom fonts unavailable."""
    try:
        name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(name, size)
    except Exception:
        try:
            return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
        except Exception:
            return ImageFont.load_default()


def _draw_header(draw, y, clinic, doctor, reg, addr, width):
    hf = _get_font(20, True)
    nf = _get_font(14)
    sf = _get_font(12)
    draw.text((width // 2, y), clinic, fill="#1a237e", font=hf, anchor="mt")
    y += 28
    draw.text((width // 2, y), doctor, fill="#333", font=nf, anchor="mt")
    y += 20
    draw.text((width // 2, y), f"Reg. No: {reg}", fill="#555", font=sf, anchor="mt")
    y += 18
    draw.text((width // 2, y), addr, fill="#555", font=sf, anchor="mt")
    y += 25
    draw.line([(40, y), (width - 40, y)], fill="#1a237e", width=2)
    return y + 10


def generate_prescription(data: dict, filename: str) -> str:
    w, h = 800, 1100
    img = Image.new("RGB", (w, h), "#FFFEF7")
    d = ImageDraw.Draw(img)
    nf, sf, bf = _get_font(14), _get_font(12), _get_font(14, True)

    y = _draw_header(d, 30, data.get("clinic", "City Health Clinic"),
                     data.get("doctor", "Dr. Sharma, MBBS, MD"),
                     data.get("reg", "KA/45678/2015"),
                     data.get("address", "123 MG Road, Bangalore - 560001"), w)

    d.text((50, y), f"Date: {data.get('date', '01/11/2024')}", fill="#333", font=nf); y += 25
    d.line([(40, y), (w - 40, y)], fill="#ccc", width=1); y += 15
    d.text((50, y), f"Patient Name: {data.get('patient', 'Rajesh Kumar')}", fill="#333", font=bf); y += 22
    d.text((50, y), f"Age/Sex: {data.get('age_sex', '35/M')}", fill="#333", font=nf); y += 30

    d.text((50, y), "Chief Complaints:", fill="#1a237e", font=bf); y += 22
    for c in data.get("complaints", ["Fever for 3 days", "Body ache", "Headache"]):
        d.text((70, y), f"• {c}", fill="#333", font=nf); y += 20
    y += 10

    d.text((50, y), "Diagnosis:", fill="#1a237e", font=bf); y += 22
    d.text((70, y), data.get("diagnosis", "Viral Fever"), fill="#333", font=nf); y += 30

    d.text((50, y), "Rx", fill="#1a237e", font=_get_font(22, True)); y += 30
    for i, med in enumerate(data.get("medicines", [
        {"name": "Tab. Paracetamol 650mg", "dosage": "1-0-1", "duration": "5 days"},
        {"name": "Tab. Vitamin C 500mg", "dosage": "1-0-0", "duration": "10 days"}
    ]), 1):
        d.text((70, y), f"{i}. {med['name']}", fill="#333", font=bf); y += 20
        d.text((90, y), f"   {med['dosage']} x {med['duration']}", fill="#555", font=sf); y += 22

    y += 10
    if data.get("tests"):
        d.text((50, y), "Investigations Advised:", fill="#1a237e", font=bf); y += 22
        for t in data["tests"]:
            d.text((70, y), f"• {t}", fill="#333", font=nf); y += 20

    y += 20
    d.text((50, y), f"Follow-up: {data.get('followup', 'After 5 days')}", fill="#555", font=sf); y += 40
    d.line([(40, y), (w - 40, y)], fill="#ccc", width=1); y += 15
    d.text((w - 200, y), data.get("doctor_short", "Dr. Sharma"), fill="#333", font=bf)
    d.text((w - 200, y + 20), "[Signature & Stamp]", fill="#888", font=sf)

    path = os.path.join(OUTPUT_DIR, filename)
    img.save(path, quality=95)
    return path


def generate_bill(data: dict, filename: str) -> str:
    w, h = 800, 900
    img = Image.new("RGB", (w, h), "#FFFFFF")
    d = ImageDraw.Draw(img)
    nf, sf, bf = _get_font(14), _get_font(12), _get_font(14, True)
    hf = _get_font(20, True)

    y = 30
    d.text((w // 2, y), data.get("hospital", "City Health Clinic"), fill="#1a237e", font=hf, anchor="mt"); y += 28
    d.text((w // 2, y), data.get("address", "123 MG Road, Bangalore"), fill="#555", font=sf, anchor="mt"); y += 18
    d.text((w // 2, y), f"GST No: {data.get('gst', '29AABCT1234F1Z5')}", fill="#555", font=sf, anchor="mt"); y += 25
    d.line([(40, y), (w - 40, y)], fill="#1a237e", width=2); y += 15

    bill_no = data.get("bill_no", "BL-2024-0847")
    d.text((50, y), f"Bill No: {bill_no}", fill="#333", font=nf)
    d.text((w - 250, y), f"Date: {data.get('date', '01/11/2024')}", fill="#333", font=nf); y += 30
    d.text((50, y), f"Patient: {data.get('patient', 'Rajesh Kumar')}", fill="#333", font=bf); y += 22
    d.text((50, y), f"Ref. By: {data.get('doctor', 'Dr. Sharma')}", fill="#555", font=nf); y += 30

    d.line([(50, y), (w - 50, y)], fill="#333", width=1); y += 5
    d.text((50, y), "PARTICULARS", fill="#1a237e", font=bf)
    d.text((w - 150, y), "AMOUNT (₹)", fill="#1a237e", font=bf); y += 22
    d.line([(50, y), (w - 50, y)], fill="#333", width=1); y += 10

    total = 0
    for item in data.get("items", [
        {"desc": "Consultation Fee", "amount": 1000},
        {"desc": "CBC Test", "amount": 300},
        {"desc": "Dengue NS1 Antigen Test", "amount": 200}
    ]):
        d.text((50, y), item["desc"], fill="#333", font=nf)
        d.text((w - 150, y), f"₹ {item['amount']:,.0f}", fill="#333", font=nf, anchor="lt"); y += 22
        total += item["amount"]

    y += 10
    d.line([(50, y), (w - 50, y)], fill="#333", width=1); y += 10
    d.text((50, y), "TOTAL", fill="#1a237e", font=bf)
    d.text((w - 150, y), f"₹ {total:,.0f}", fill="#1a237e", font=bf); y += 30
    d.text((50, y), f"Payment Mode: {data.get('payment', 'UPI')}", fill="#555", font=nf); y += 30
    d.line([(50, y), (w - 50, y)], fill="#ccc", width=1); y += 15
    d.text((w - 200, y), "[Authorized Signatory]", fill="#888", font=sf)

    path = os.path.join(OUTPUT_DIR, filename)
    img.save(path, quality=95)
    return path


def generate_all_test_documents():
    """Generate documents matching all 10 test cases."""
    docs = {}

    # TC001 — Simple Consultation
    docs["tc001_prescription"] = generate_prescription({
        "clinic": "City Health Clinic", "doctor": "Dr. Sharma, MBBS, MD",
        "reg": "KA/45678/2015", "address": "45 Jayanagar, Bangalore - 560041",
        "date": "01/11/2024", "patient": "Rajesh Kumar", "age_sex": "35/M",
        "complaints": ["Fever for 3 days", "Body ache", "Headache"],
        "diagnosis": "Viral Fever",
        "medicines": [
            {"name": "Tab. Paracetamol 650mg", "dosage": "1-0-1", "duration": "5 days"},
            {"name": "Tab. Vitamin C 500mg", "dosage": "1-0-0", "duration": "10 days"}
        ],
        "tests": ["CBC", "Dengue NS1 Antigen Test"], "followup": "After 5 days",
        "doctor_short": "Dr. Sharma"
    }, "tc001_prescription.png")

    docs["tc001_bill"] = generate_bill({
        "hospital": "City Health Clinic", "address": "45 Jayanagar, Bangalore",
        "date": "01/11/2024", "patient": "Rajesh Kumar", "doctor": "Dr. Sharma",
        "items": [{"desc": "Consultation Fee", "amount": 1000},
                  {"desc": "CBC Test", "amount": 300}, {"desc": "Dengue NS1 Test", "amount": 200}],
        "payment": "UPI"
    }, "tc001_bill.png")

    # TC002 — Dental
    docs["tc002_prescription"] = generate_prescription({
        "clinic": "Smile Dental Care", "doctor": "Dr. Patel, BDS, MDS",
        "reg": "MH/23456/2018", "address": "78 Bandra West, Mumbai - 400050",
        "date": "15/10/2024", "patient": "Priya Singh", "age_sex": "28/F",
        "complaints": ["Severe toothache", "Sensitivity to hot/cold"],
        "diagnosis": "Tooth decay requiring root canal",
        "medicines": [{"name": "Tab. Amoxicillin 500mg", "dosage": "1-0-1", "duration": "5 days"},
                      {"name": "Tab. Ibuprofen 400mg", "dosage": "1-0-1", "duration": "3 days"}],
        "tests": [], "followup": "After 1 week", "doctor_short": "Dr. Patel"
    }, "tc002_prescription.png")

    docs["tc002_bill"] = generate_bill({
        "hospital": "Smile Dental Care", "address": "78 Bandra West, Mumbai",
        "date": "15/10/2024", "patient": "Priya Singh", "doctor": "Dr. Patel",
        "items": [{"desc": "Root Canal Treatment", "amount": 8000},
                  {"desc": "Teeth Whitening (Cosmetic)", "amount": 4000}],
        "payment": "Card"
    }, "tc002_bill.png")

    # TC003 — Limit Exceeded
    docs["tc003_prescription"] = generate_prescription({
        "clinic": "Delhi Medical Centre", "doctor": "Dr. Gupta, MBBS, MD (Medicine)",
        "reg": "DL/34567/2016", "address": "Connaught Place, New Delhi - 110001",
        "date": "20/10/2024", "patient": "Amit Verma", "age_sex": "42/M",
        "complaints": ["Loose motions for 2 days", "Abdominal cramps", "Nausea"],
        "diagnosis": "Gastroenteritis",
        "medicines": [{"name": "Tab. Ofloxacin 200mg", "dosage": "1-0-1", "duration": "5 days"},
                      {"name": "Cap. Probiotics", "dosage": "1-0-1", "duration": "14 days"},
                      {"name": "Sachet ORS", "dosage": "As required", "duration": "5 days"}],
        "doctor_short": "Dr. Gupta"
    }, "tc003_prescription.png")

    docs["tc003_bill"] = generate_bill({
        "hospital": "Delhi Medical Centre", "date": "20/10/2024", "patient": "Amit Verma",
        "doctor": "Dr. Gupta",
        "items": [{"desc": "Consultation Fee", "amount": 2000},
                  {"desc": "Medicines (Antibiotics + Probiotics)", "amount": 5500}],
        "payment": "Cash"
    }, "tc003_bill.png")

    # TC005 — Diabetes / Waiting Period
    docs["tc005_prescription"] = generate_prescription({
        "clinic": "Mehta Diabetes Care", "doctor": "Dr. Mehta, MBBS, MD (Endocrinology)",
        "reg": "GJ/56789/2014", "address": "SG Highway, Ahmedabad - 380054",
        "date": "15/10/2024", "patient": "Vikram Joshi", "age_sex": "45/M",
        "complaints": ["Increased thirst", "Frequent urination", "Fatigue"],
        "diagnosis": "Type 2 Diabetes",
        "medicines": [{"name": "Tab. Metformin 500mg", "dosage": "1-0-1", "duration": "30 days"},
                      {"name": "Tab. Glimepiride 1mg", "dosage": "1-0-0", "duration": "30 days"}],
        "tests": ["HbA1c", "Fasting Blood Sugar"], "doctor_short": "Dr. Mehta"
    }, "tc005_prescription.png")

    docs["tc005_bill"] = generate_bill({
        "hospital": "Mehta Diabetes Care", "date": "15/10/2024", "patient": "Vikram Joshi",
        "doctor": "Dr. Mehta",
        "items": [{"desc": "Consultation Fee", "amount": 1000}, {"desc": "Medicines", "amount": 2000}],
        "payment": "UPI"
    }, "tc005_bill.png")

    # TC006 — Alternative Medicine
    docs["tc006_prescription"] = generate_prescription({
        "clinic": "Kerala Ayurveda Centre", "doctor": "Vaidya Krishnan, BAMS",
        "reg": "AYUR/KL/2345/2019", "address": "MG Road, Kochi - 682016",
        "date": "28/10/2024", "patient": "Kavita Nair", "age_sex": "38/F",
        "complaints": ["Chronic joint pain", "Stiffness in mornings"],
        "diagnosis": "Chronic joint pain - Sandhivata",
        "medicines": [{"name": "Maharasnadi Kashayam", "dosage": "15ml-0-15ml", "duration": "30 days"},
                      {"name": "Kottamchukkadi Tailam", "dosage": "External", "duration": "As needed"}],
        "tests": [], "followup": "After 2 weeks", "doctor_short": "Vaidya Krishnan"
    }, "tc006_prescription.png")

    docs["tc006_bill"] = generate_bill({
        "hospital": "Kerala Ayurveda Centre", "date": "28/10/2024", "patient": "Kavita Nair",
        "doctor": "Vaidya Krishnan",
        "items": [{"desc": "Consultation Fee", "amount": 1000},
                  {"desc": "Panchakarma Therapy (2 sessions)", "amount": 3000}],
        "payment": "Cash"
    }, "tc006_bill.png")

    # TC009 — Weight Loss (Excluded)
    docs["tc009_prescription"] = generate_prescription({
        "clinic": "Wellness & Weight Clinic", "doctor": "Dr. Banerjee, MBBS, MD",
        "reg": "WB/34567/2015", "address": "Park Street, Kolkata - 700016",
        "date": "18/10/2024", "patient": "Anita Desai", "age_sex": "29/F",
        "complaints": ["Weight gain", "Difficulty in weight management"],
        "diagnosis": "Obesity - BMI 35",
        "medicines": [{"name": "Tab. Orlistat 120mg", "dosage": "1-1-1", "duration": "30 days"}],
        "doctor_short": "Dr. Banerjee"
    }, "tc009_prescription.png")

    docs["tc009_bill"] = generate_bill({
        "hospital": "Wellness & Weight Clinic", "date": "18/10/2024", "patient": "Anita Desai",
        "doctor": "Dr. Banerjee",
        "items": [{"desc": "Bariatric Consultation", "amount": 3000},
                  {"desc": "Personalized Diet Plan", "amount": 5000}],
        "payment": "Card"
    }, "tc009_bill.png")

    # TC010 — Network Hospital
    docs["tc010_prescription"] = generate_prescription({
        "clinic": "Apollo Hospitals", "doctor": "Dr. Iyer, MBBS, MD (Pulmonology)",
        "reg": "TN/56789/2013", "address": "Greams Road, Chennai - 600006",
        "date": "03/11/2024", "patient": "Deepak Shah", "age_sex": "36/M",
        "complaints": ["Persistent cough for 1 week", "Mild breathlessness"],
        "diagnosis": "Acute Bronchitis",
        "medicines": [{"name": "Tab. Azithromycin 500mg", "dosage": "1-0-0", "duration": "3 days"},
                      {"name": "Inhaler Salbutamol", "dosage": "2 puffs PRN", "duration": "As needed"}],
        "tests": ["Chest X-Ray"], "doctor_short": "Dr. Iyer"
    }, "tc010_prescription.png")

    docs["tc010_bill"] = generate_bill({
        "hospital": "Apollo Hospitals", "address": "Greams Road, Chennai",
        "date": "03/11/2024", "patient": "Deepak Shah", "doctor": "Dr. Iyer",
        "items": [{"desc": "Consultation Fee", "amount": 1500}, {"desc": "Medicines", "amount": 3000}],
        "payment": "Cashless"
    }, "tc010_bill.png")

    print(f"[OK] Generated {len(docs)} mock documents in {OUTPUT_DIR}")
    return docs


if __name__ == "__main__":
    generate_all_test_documents()
