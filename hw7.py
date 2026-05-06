class Course:
    """
    Represents a course with grading categories.

    Attributes:
        name (str): Name of the course.
        categories (list): List of category dicts with keys:
                           'name' (str), 'weight' (float), 'scores' (list of floats),
                           'drop_lowest' (bool)
    """

    def __init__(self, name):
        self.name = name
        self.categories = []

    def add_category(self, name, weight, scores, drop_lowest=False):
        """
        Adds a grading category.
        scores: list of floats already converted to 0-100 percentages.
        """
        self.categories.append({
            'name': name,
            'weight': weight,
            'scores': scores,
            'drop_lowest': drop_lowest
        })

    def validate_weights(self):
        return sum(c['weight'] for c in self.categories) == 100


class GradeCalculator:
    """
    Computes grade statistics for a given Course.
    """

    def __init__(self, course):
        self.course = course

    def category_average(self, category):
        scores = list(category['scores'])
        if not scores:
            return 0.0
        if category['drop_lowest'] and len(scores) > 1:
            scores = sorted(scores)[1:]
        return sum(scores) / len(scores)

    def overall_grade(self):
        total = 0.0
        for cat in self.course.categories:
            avg = self.category_average(cat)
            total += avg * (cat['weight'] / 100)
        return total

    def whatif_score(self, target_grade, future_weight):
        current_contribution = self.overall_grade()
        needed = (target_grade - current_contribution) / (future_weight / 100)
        return {
            'needed_score': needed,
            'impossible': needed > 100
        }


def compute_panic_score(current_score, exam_date_days_away, hours_studied, total_hours_needed=10):
    grade_risk    = (100 - current_score) / 100
    time_pressure = 1 / max(exam_date_days_away, 1)
    study_deficit = max(0, (total_hours_needed - hours_studied) / total_hours_needed)
    return grade_risk * time_pressure * study_deficit * 100


def rank_exams(exams):
    for exam in exams:
        exam['panic_score'] = compute_panic_score(
            exam['current_score'],
            exam['days_away'],
            exam['hours_studied']
        )
    return sorted(exams, key=lambda e: e['panic_score'], reverse=True)
