
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3, os, random
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("NOVA_SECRET", "nova-dev-key-change-before-deployment")
DB = os.path.join(os.path.dirname(__file__), "nova.db")

SAMPLE_QUESTIONS = [
    ("Life Science", "Cells", "What is the basic structural and functional unit of life?", ["Atom", "Cell", "Tissue", "Organ"], 1, "The cell is the basic structural and functional unit of life."),
    ("Life Science", "Cells", "Which structure controls most activities of a cell?", ["Cell wall", "Nucleus", "Cytoplasm", "Vacuole"], 1, "The nucleus contains genetic material and controls cell activities."),
    ("Life Science", "Human Body", "Which organ pumps blood around the human body?", ["Lungs", "Heart", "Kidney", "Stomach"], 1, "The heart pumps blood through the circulatory system."),
    ("Life Science", "Plants", "Which plant part mainly absorbs water from the soil?", ["Flower", "Leaf", "Root", "Fruit"], 2, "Roots absorb water and mineral nutrients from the soil."),
    ("Physical Science", "Matter", "Which state of matter has a fixed volume but no fixed shape?", ["Solid", "Liquid", "Gas", "None"], 1, "A liquid has a fixed volume and takes the shape of its container."),
    ("Physical Science", "Forces", "What is the SI unit of force?", ["Joule", "Watt", "Newton", "Metre"], 2, "Force is measured in newtons (N)."),
    ("Physical Science", "Energy", "What is the main source of energy for Earth?", ["The Moon", "The Sun", "Wind", "The ocean"], 1, "The Sun is the primary source of energy for most processes on Earth."),
    ("Physical Science", "Chemistry", "What is the chemical formula for water?", ["CO2", "O2", "H2O", "NaCl"], 2, "A water molecule contains two hydrogen atoms and one oxygen atom."),
    ("Earth & Space", "Solar System", "Which planet is often called the Red Planet?", ["Venus", "Mars", "Jupiter", "Mercury"], 1, "Mars appears reddish because of iron oxide on its surface."),
    ("Earth & Space", "Environment", "Which gas do plants absorb during photosynthesis?", ["Oxygen", "Carbon dioxide", "Nitrogen", "Helium"], 1, "Plants use carbon dioxide, water and light to make sugars."),
    ("Earth & Space", "Environment", "Which action helps reduce soil erosion?", ["Removing vegetation", "Overgrazing", "Planting trees", "Burning forests"], 2, "Plant roots hold soil together and reduce erosion."),
    ("Physical Science", "Electricity", "Which device opens or closes an electric circuit?", ["Switch", "Bulb", "Wire", "Battery"], 0, "A switch controls whether a circuit is open or closed."),
]


ALL_SUBJECT_QUESTIONS = [
    ("Mathematics","Numbers","What is 25% of 200?",["25","40","50","75"],2,"25% means one quarter; 200 ÷ 4 = 50."),
    ("Mathematics","Algebra","If x + 7 = 12, what is x?",["3","5","7","19"],1,"Subtract 7 from both sides: x = 5."),
    ("English","Grammar","Which word is a noun in 'The child reads'?",["quickly","reads","child","the"],2,"Child names a person, so it is a noun."),
    ("English","Vocabulary","Which word is closest in meaning to 'rapid'?",["slow","fast","quiet","weak"],1,"Rapid means fast or quick."),
    ("Amharic","ቋንቋ","በአማርኛ የስም ቃል ምንን ይገልጻል?",["ተግባር","ሰው፣ ቦታ ወይም ነገር","ጊዜ","ቀለም"],1,"ስም ሰውን፣ ቦታን ወይም ነገርን ይገልጻል።"),
    ("Social Studies","Geography","Which imaginary line divides Earth into Northern and Southern Hemispheres?",["Prime Meridian","Equator","Tropic of Cancer","International Date Line"],1,"The Equator is at 0° latitude."),
    ("Civics & Ethics","Rights","Which is an example of a civic responsibility?",["Ignoring laws","Protecting public property","Damaging roads","Denying others' rights"],1,"Citizens share responsibility for protecting public resources."),
    ("Health Education","Hygiene","What is an effective way to reduce the spread of many germs?",["Sharing cups","Washing hands with soap","Avoiding clean water","Touching the face often"],1,"Handwashing with soap removes many germs."),
    ("ICT","Computers","Which component is often called the brain of a computer?",["Monitor","Keyboard","CPU","Mouse"],2,"The CPU processes instructions and data."),
    ("Agriculture","Plants","Which soil component is formed from decayed organic matter?",["Humus","Gravel","Plastic","Metal"],0,"Humus is decomposed organic material that improves soil."),
]

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS questions(
            id INTEGER PRIMARY KEY AUTOINCREMENT, subject TEXT, chapter TEXT,
            question TEXT, options TEXT, answer INTEGER, explanation TEXT)""")
        con.execute("""CREATE TABLE IF NOT EXISTS results(
            id INTEGER PRIMARY KEY AUTOINCREMENT, student TEXT, score INTEGER,
            total INTEGER, percent INTEGER, created_at TEXT)""")
        count = con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        if count == 0:
            import json
            seed = SAMPLE_QUESTIONS + ALL_SUBJECT_QUESTIONS
            for subject, chapter, q, opts, ans, exp in seed:
                con.execute("INSERT INTO questions(subject,chapter,question,options,answer,explanation) VALUES(?,?,?,?,?,?)",
                            (subject, chapter, q, json.dumps(opts), ans, exp))
        else:
            import json
            existing = {(r[0], r[1]) for r in con.execute("SELECT subject, question FROM questions")}
            for subject, chapter, q, opts, ans, exp in ALL_SUBJECT_QUESTIONS:
                if (subject, q) not in existing:
                    con.execute("INSERT INTO questions(subject,chapter,question,options,answer,explanation) VALUES(?,?,?,?,?,?)",
                                (subject, chapter, q, json.dumps(opts), ans, exp))

@app.route("/")
def home():
    with connect() as con:
        total = con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        chapters = con.execute("SELECT COUNT(DISTINCT chapter) FROM questions").fetchone()[0]
        recent = con.execute("SELECT student, score, total, percent FROM results ORDER BY id DESC LIMIT 5").fetchall()
    subjects = ["Mathematics", "English", "Amharic", "General Science", "Social Studies",
                "Civics & Ethics", "Health Education", "ICT", "Agriculture"]
    return render_template("index.html", total=total, chapters=chapters, recent=recent, subjects=subjects)

@app.route("/quiz")
def quiz():
    import json
    subject = request.args.get("subject", "All")
    with connect() as con:
        if subject == "All":
            rows = con.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 10").fetchall()
        else:
            rows = con.execute("SELECT * FROM questions WHERE subject=? ORDER BY RANDOM() LIMIT 10", (subject,)).fetchall()
            if not rows and subject == "General Science":
                rows = con.execute("SELECT * FROM questions WHERE subject IN ('Life Science','Physical Science','Earth & Space') ORDER BY RANDOM() LIMIT 10").fetchall()
    questions = []
    for r in rows:
        questions.append({"id":r["id"], "subject":r["subject"], "chapter":r["chapter"],
                          "question":r["question"], "options":json.loads(r["options"]),
                          "answer":r["answer"], "explanation":r["explanation"]})
    if not questions:
        return redirect(url_for("home"))
    session["quiz_questions"] = questions
    session["quiz_name"] = request.args.get("name", "Student")[:30]
    return render_template("quiz.html", questions=questions)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json(silent=True) or {}
    questions = session.get("quiz_questions", [])
    answers = data.get("answers", {})
    student = session.get("quiz_name", "Student")
    score = sum(1 for q in questions if str(q["id"]) in answers and int(answers[str(q["id"])]) == q["answer"])
    total = len(questions)
    percent = round(score / total * 100) if total else 0
    with connect() as con:
        con.execute("INSERT INTO results(student,score,total,percent,created_at) VALUES(?,?,?,?,?)",
                    (student, score, total, percent, datetime.now().strftime("%Y-%m-%d %H:%M")))
    review = []
    for q in questions:
        chosen = answers.get(str(q["id"]))
        review.append({"question":q["question"], "options":q["options"], "answer":q["answer"],
                       "chosen":int(chosen) if chosen is not None else None,
                       "explanation":q["explanation"]})
    session.pop("quiz_questions", None)
    return jsonify({"score":score, "total":total, "percent":percent, "review":review})

@app.route("/leaderboard")
def leaderboard():
    with connect() as con:
        rows = con.execute("""SELECT student, MAX(percent) AS best, COUNT(*) AS attempts
                              FROM results GROUP BY student ORDER BY best DESC LIMIT 20""").fetchall()
    return render_template("leaderboard.html", rows=rows)

@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    if request.method == "POST":
        subject = request.form["subject"].strip()
        chapter = request.form["chapter"].strip()
        question = request.form["question"].strip()
        options = [request.form.get(f"option{i}", "").strip() for i in range(4)]
        answer = int(request.form["answer"])
        explanation = request.form.get("explanation", "").strip()
        import json
        if all([subject, chapter, question]) and all(options):
            with connect() as con:
                con.execute("INSERT INTO questions(subject,chapter,question,options,answer,explanation) VALUES(?,?,?,?,?,?)",
                            (subject, chapter, question, json.dumps(options), answer, explanation))
            return render_template("add_question.html", success="Question added successfully!")
        return render_template("add_question.html", error="Please complete all required fields.")
    return render_template("add_question.html")


TUTOR_LIBRARY = {
 "cells": ("General Science","Cells","Cells are the basic structural and functional units of living things. Many organisms are made of one cell, while plants and animals are made of many cells. The cell membrane controls what enters and leaves; the cytoplasm is where many reactions happen; and the nucleus stores DNA and helps control cell activities.",
 ["Cell membrane controls movement of materials","Cytoplasm contains cell structures","Nucleus contains genetic information"]),
 "photosynthesis": ("General Science","Photosynthesis","Photosynthesis is the process by which green plants use light energy to make glucose from carbon dioxide and water. It mainly happens in chloroplasts, which contain chlorophyll. Oxygen is released as a product.",
 ["Plants need light, water and carbon dioxide","Chlorophyll absorbs light energy","Glucose stores chemical energy"]),
 "force": ("General Science","Force and Motion","A force is a push or pull that can change an object's motion, direction or shape. The SI unit of force is the newton (N). Balanced forces do not change an object's motion; unbalanced forces cause acceleration.",
 ["Force is measured in newtons","Balanced forces have zero net force","Unbalanced forces can change motion"]),
 "energy": ("General Science","Energy","Energy is the ability to cause change or do work. Common forms include kinetic, potential, thermal, chemical, electrical and light energy. Energy can be transferred or transformed, but it is conserved.",
 ["Kinetic energy is energy of motion","Potential energy is stored energy","Energy changes form but is conserved"]),
 "matter": ("General Science","States of Matter","Matter is anything that has mass and occupies space. Solids have a fixed shape and volume, liquids have a fixed volume but take the shape of their container, and gases spread to fill their container.",
 ["Solids have fixed shape and volume","Liquids have fixed volume","Gases expand to fill their container"]),
 "solar": ("General Science","Solar System","The Solar System consists of the Sun and objects held by its gravity, including eight planets, dwarf planets, moons, asteroids and comets. Planets orbit the Sun.",
 ["The Sun is a star","Eight planets orbit the Sun","Gravity keeps planets in orbit"]),
 "electricity": ("General Science","Electricity","Electric current is the flow of electric charge. A simple circuit needs a source of electrical energy, conducting wires and a complete path. A switch opens or closes the circuit.",
 ["Current is measured in amperes","A closed circuit allows current to flow","A switch controls the circuit"]),
 "water": ("General Science","Water Cycle","The water cycle is the continuous movement of water through evaporation, condensation, precipitation and collection. Sunlight drives evaporation, and gravity helps water return to Earth's surface.",
 ["Evaporation changes liquid water to vapor","Condensation forms droplets and clouds","Precipitation returns water to Earth"]),
 "fractions": ("Mathematics","Fractions","A fraction represents part of a whole. The numerator counts selected parts and the denominator counts equal parts in the whole. Equivalent fractions have the same value.",
 ["Denominator cannot be zero","Equivalent fractions have equal values","Simplify by dividing numerator and denominator by a common factor"]),
 "algebra": ("Mathematics","Algebra","Algebra uses letters such as x to represent unknown numbers. To solve an equation, keep it balanced by doing the same operation to both sides.",
 ["A variable represents a number","Use inverse operations to solve equations","Do the same operation to both sides"]),
 "grammar": ("English","Grammar","Grammar describes how words are arranged to make meaningful sentences. A noun names a person, place, thing or idea; a verb expresses an action or state; and an adjective describes a noun.",
 ["Nouns name people, places, things or ideas","Verbs express actions or states","Adjectives describe nouns"]),
 "reading": ("English","Reading Comprehension","Reading comprehension means understanding a text. Identify the main idea, notice supporting details, use context to understand unfamiliar words, and make conclusions supported by the passage.",
 ["Find the main idea","Use details as evidence","Use context to understand vocabulary"]),
 "amharic": ("Amharic","የአማርኛ ቋንቋ","አማርኛ በኢትዮጵያ በስፋት የሚነገር ቋንቋ ነው። ቃላት በዓረፍተ ነገር ውስጥ ተደራጅተው ትርጉም ይፈጥራሉ። ስም ሰውን፣ ቦታን፣ ነገርን ወይም ሐሳብን ይገልጻል።",
 ["ስም ሰውን፣ ቦታን ወይም ነገርን ይገልጻል","ግስ ተግባርን ወይም ሁኔታን ይገልጻል","ዓረፍተ ነገር ሙሉ ሐሳብን ያቀርባል"]),
 "geography": ("Social Studies","Geography","Geography studies Earth's places, environments and the relationships between people and their surroundings. Maps use symbols, scale and direction to represent real places.",
 ["Maps represent places","The Equator is 0° latitude","Physical and human geography are connected"]),
 "civics": ("Civics & Ethics","Citizenship","Citizenship includes rights and responsibilities. Good citizens respect others, follow fair laws, participate in their communities and help protect public property.",
 ["Rights come with responsibilities","Respect others' rights","Protect shared resources"]),
 "health": ("Health Education","Personal Hygiene","Personal hygiene means habits that keep the body clean and help prevent illness. Washing hands with soap, using safe water, brushing teeth and keeping food clean are useful practices.",
 ["Wash hands with soap","Drink safe water","Keep food and surroundings clean"]),
 "computer": ("ICT","Computer Basics","A computer is an electronic device that accepts input, processes data, stores information and produces output. The CPU processes instructions, while input and output devices help people interact with it.",
 ["Input devices send data","CPU processes instructions","Output devices present results"]),
 "soil": ("Agriculture","Soil","Soil supports plant growth by providing anchorage, water and minerals. Healthy soil contains mineral particles, organic matter, air and water. Compost can add organic matter.",
 ["Soil supports roots","Humus comes from decayed organic matter","Conservation reduces erosion"])
}
QUIZ_LIBRARY = {
 "cells":[("Which part controls what enters and leaves a cell?",["Cell membrane","Nucleus","Ribosome","Vacuole"],0,"The cell membrane regulates movement in and out."),
 ("Where is most of a cell's DNA stored?",["Cell wall","Nucleus","Cytoplasm","Membrane"],1,"The nucleus stores most genetic information.")],
 "photosynthesis":[("Which gas do plants take in for photosynthesis?",["Oxygen","Nitrogen","Carbon dioxide","Hydrogen"],2,"Carbon dioxide is used to make glucose."),
 ("What pigment absorbs light for photosynthesis?",["Hemoglobin","Chlorophyll","Melanin","Keratin"],1,"Chlorophyll absorbs light energy.")],
 "force":[("What is the SI unit of force?",["Joule","Newton","Watt","Pascal"],1,"Force is measured in newtons."),
 ("What happens when forces are balanced?",["Net force is zero","Object must speed up","Mass disappears","Gravity stops"],0,"Balanced forces produce zero net force.")],
 "energy":[("Which is energy of motion?",["Potential","Chemical","Kinetic","Nuclear"],2,"Kinetic energy is energy of motion.")],
 "matter":[("Which state has a fixed volume but no fixed shape?",["Solid","Liquid","Gas","Plasma"],1,"Liquids keep volume but take container shape.")],
 "solar":[("How many planets orbit the Sun in our Solar System?",["Seven","Eight","Nine","Ten"],1,"There are eight recognized planets.")],
 "electricity":[("Which component opens or closes a circuit?",["Switch","Wire","Bulb","Resistor"],0,"A switch opens or closes the path.")],
 "water":[("What is the process called when liquid water becomes vapor?",["Condensation","Precipitation","Evaporation","Collection"],2,"Evaporation changes liquid water to vapor.")],
 "fractions":[("What is 1/2 + 1/4?",["1/4","2/6","3/4","1"],2,"1/2 is 2/4, and 2/4 + 1/4 = 3/4.")],
 "algebra":[("If x + 7 = 12, what is x?",["3","5","7","19"],1,"Subtract 7 from both sides: x = 5.")],
 "grammar":[("Which word is a noun in 'The child reads'?",["quickly","reads","child","the"],2,"Child names a person.")],
 "reading":[("What is the main idea of a passage?",["A small detail","The central message","The page number","The author's name"],1,"The main idea is the central point.")],
 "amharic":[("በአማርኛ የስም ቃል ምንን ይገልጻል?",["ተግባር","ሰው፣ ቦታ ወይም ነገር","ጊዜ","ቀለም"],1,"ስም ሰውን፣ ቦታን ወይም ነገርን ይገልጻል።")],
 "geography":[("Which line divides Earth into Northern and Southern Hemispheres?",["Equator","Prime Meridian","Tropic of Capricorn","Arctic Circle"],0,"The Equator is at 0° latitude.")],
 "civics":[("Which is a civic responsibility?",["Damaging public property","Respecting others' rights","Ignoring laws","Blocking public services"],1,"Respecting rights is part of responsible citizenship.")],
 "health":[("Which habit helps reduce the spread of germs?",["Sharing cups","Handwashing with soap","Skipping bathing","Using dirty water"],1,"Soap and water remove many germs.")],
 "computer":[("What does CPU stand for?",["Central Processing Unit","Computer Personal Utility","Central Program User","Control Power Unit"],0,"CPU means Central Processing Unit.")],
 "soil":[("What is humus?",["Decayed organic matter","Crushed plastic","Pure sand","Metal particles"],0,"Humus is decomposed organic matter.")]
}
TOPIC_KEYS = {
 "cells":"cells","cell":"cells","photosynthesis":"photosynthesis","plant food":"photosynthesis",
 "force":"force","motion":"force","energy":"energy","matter":"matter","solid":"matter","liquid":"matter",
 "solar":"solar","planet":"solar","electric":"electricity","circuit":"electricity","water cycle":"water",
 "fraction":"fractions","math":"fractions","algebra":"algebra","equation":"algebra",
 "grammar":"grammar","noun":"grammar","reading":"reading","comprehension":"reading",
 "amharic":"amharic","አማርኛ":"amharic","ስም":"amharic",
 "geography":"geography","map":"geography","civics":"civics","citizen":"civics",
 "health":"health","hygiene":"health","computer":"computer","ict":"computer","soil":"soil","agriculture":"soil"
}
def topic_key(text):
    low = (text or "").lower()
    for needle, key in TOPIC_KEYS.items():
        if needle in low: return key
    return None

@app.route("/tutor")
def tutor():
    return render_template("tutor.html")

@app.route("/api/tutor", methods=["POST"])
def api_tutor():
    import random
    data = request.get_json(silent=True) or {}
    action = data.get("action", "explain")
    key = data.get("topic") if action == "quiz" else topic_key(data.get("message", ""))
    if not key or key not in TUTOR_LIBRARY:
        return jsonify({"type":"reply","reply":"I can teach topics across Mathematics, English, Amharic, General Science, Social Studies, Civics & Ethics, Health Education, ICT and Agriculture. Try a topic such as fractions, grammar, አማርኛ, cells, geography, hygiene, computers or soil."})
    if action == "quiz":
        qs = QUIZ_LIBRARY.get(key, [])
        random.shuffle(qs)
        return jsonify({"type":"quiz","topic":key,"questions":[{"q":q,"options":o,"answer":a,"why":e} for q,o,a,e in qs[:5]]})
    subject,title,explanation,points = TUTOR_LIBRARY[key]
    return jsonify({"type":"lesson","topic":key,"subject":subject,"title":title,"explanation":explanation,"key_points":points})


@app.route("/health")
def health():
    return {"status":"ok"}

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("FLASK_DEBUG") == "1")
