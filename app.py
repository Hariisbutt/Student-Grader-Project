from flask import Flask, request, jsonify, render_template
import hw7
import json
import os

app = Flask(__name__)

# ── In-memory course store (persisted to a JSON sidecar file) ─────────────
STORE_FILE = os.path.join(os.path.dirname(__file__), 'courses_store.json')


def load_store():
    if os.path.exists(STORE_FILE):
        try:
            with open(STORE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_store(store):
    with open(STORE_FILE, 'w') as f:
        json.dump(store, f, indent=2)


# ── Helper: convert raw assignment scores to percentages ──────────────────
def raw_scores_to_pct(assignments):
    """
    assignments: list of dicts with 'earned' (float) and 'max' (float).
    Returns list of percentage floats (0–100).
    Skips assignments with max=0 to avoid division by zero.
    """
    pcts = []
    for a in assignments:
        mx = float(a.get('max', 100))
        earned = float(a.get('earned', 0))
        if mx > 0:
            pcts.append((earned / mx) * 100)
    return pcts


def apply_best_of(scores, best_of):
    """
    If best_of > 0 and best_of < len(scores), keep only the top `best_of` scores.
    Returns the filtered list.
    """
    if best_of and best_of > 0 and best_of < len(scores):
        return sorted(scores, reverse=True)[:best_of]
    return scores


def letter(g):
    if g >= 93:   return 'A'
    elif g >= 90: return 'A-'
    elif g >= 87: return 'B+'
    elif g >= 83: return 'B'
    elif g >= 80: return 'B-'
    elif g >= 77: return 'C+'
    elif g >= 73: return 'C'
    elif g >= 70: return 'C-'
    else:         return 'F'


# ── Routes ────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/grade', methods=['POST'])
def calculate_grade():
    """
    POST body:
    {
      "course_name": "CS515",
      "categories": [
        {
          "name": "Homework",
          "weight": 30,
          "drop_lowest": false,
          "best_of": 8,           // 0 = use all; N = keep best N out of total
          "assignments": [
            { "earned": 34, "max": 34 },
            { "earned": 46, "max": 48 },
            ...
          ]
        },
        ...
      ]
    }
    """
    data = request.get_json()
    course = hw7.Course(data['course_name'])

    cat_details = []
    for cat in data['categories']:
        pcts = raw_scores_to_pct(cat.get('assignments', []))
        best_of = int(cat.get('best_of', 0))
        pcts = apply_best_of(pcts, best_of)

        course.add_category(
            cat['name'],
            float(cat['weight']),
            pcts,
            cat.get('drop_lowest', False)
        )

    valid = course.validate_weights()
    calc  = hw7.GradeCalculator(course)
    overall = calc.overall_grade()

    averages = []
    for i, c in enumerate(course.categories):
        avg = calc.category_average(c)
        raw_cat = data['categories'][i]
        assignments = raw_cat.get('assignments', [])
        best_of = int(raw_cat.get('best_of', 0))
        total_submitted = len([a for a in assignments if float(a.get('max', 0)) > 0])
        averages.append({
            'name':      c['name'],
            'average':   round(avg, 2),
            'weight':    c['weight'],
            'count':     len(c['scores']),
            'total_submitted': total_submitted,
            'best_of':   best_of if best_of > 0 else None,
            'drop_lowest': c['drop_lowest'],
        })

    return jsonify({
        'valid':             valid,
        'overall_grade':     round(overall, 2),
        'letter_grade':      letter(overall),
        'category_averages': averages
    })


@app.route('/api/whatif', methods=['POST'])
def whatif():
    """
    POST body:
    {
      "categories": [ ...same format as /api/grade... ],
      "target_grade": 90,
      "future_weight": 30
    }
    """
    data = request.get_json()
    course = hw7.Course("temp")

    for cat in data['categories']:
        pcts = raw_scores_to_pct(cat.get('assignments', []))
        best_of = int(cat.get('best_of', 0))
        pcts = apply_best_of(pcts, best_of)
        course.add_category(
            cat['name'],
            float(cat['weight']),
            pcts,
            cat.get('drop_lowest', False)
        )

    calc   = hw7.GradeCalculator(course)
    result = calc.whatif_score(
        float(data['target_grade']),
        float(data['future_weight'])
    )
    result['needed_score'] = round(result['needed_score'], 2)
    return jsonify(result)


@app.route('/api/panic', methods=['POST'])
def panic():
    data   = request.get_json()
    ranked = hw7.rank_exams(data['exams'])
    for e in ranked:
        e['panic_score'] = round(e['panic_score'], 2)
    return jsonify({'ranked': ranked})


# ── Course persistence endpoints ─────────────────────────────────────────
@app.route('/api/courses', methods=['GET'])
def list_courses():
    store = load_store()
    return jsonify({'courses': list(store.keys())})


@app.route('/api/courses', methods=['POST'])
def save_course():
    data  = request.get_json()
    name  = data.get('course_name', '').strip()
    if not name:
        return jsonify({'error': 'course_name required'}), 400
    store = load_store()
    store[name] = data
    save_store(store)
    return jsonify({'saved': name, 'all_courses': list(store.keys())})


@app.route('/api/courses/<course_name>', methods=['GET'])
def get_course(course_name):
    store = load_store()
    if course_name not in store:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(store[course_name])


@app.route('/api/courses/<course_name>', methods=['DELETE'])
def delete_course(course_name):
    store = load_store()
    if course_name in store:
        del store[course_name]
        save_store(store)
    return jsonify({'deleted': course_name, 'all_courses': list(store.keys())})


if __name__ == '__main__':
    app.run(debug=True)
