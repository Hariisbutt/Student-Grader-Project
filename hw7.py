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
        """
        Initializes a Course with a name and empty categories list.

        Args:
            name (str): The course name.
        """
        self.name = name
        self.categories = []

    def add_category(self, name, weight, scores, drop_lowest=False):
        """
        Adds a grading category to the course.

        Args:
            name (str): Category name (e.g. 'Homework', 'Midterm').
            weight (float): Percentage weight of this category (0-100).
            scores (list of float): List of scores received (0-100 each).
            drop_lowest (bool): Whether to drop the lowest score. Default False.

        Returns:
            None
        """
        pass

    def validate_weights(self):
        """
        Checks whether all category weights sum to exactly 100.

        Returns:
            bool: True if weights sum to 100, False otherwise.
        """
        pass


class GradeCalculator:
    """
    Computes grade statistics for a given Course.

    Attributes:
        course (Course): The course to calculate grades for.
    """

    def __init__(self, course):
        """
        Initializes the GradeCalculator with a Course object.

        Args:
            course (Course): A Course instance with categories.
        """
        self.course = course

    def category_average(self, category):
        """
        Computes the average score for a single category,
        dropping the lowest score if drop_lowest is True.

        Args:
            category (dict): A category dict with keys 'scores' and 'drop_lowest'.

        Returns:
            float: The average score (0-100) for the category.
                   Returns 0.0 if scores list is empty.
        """
        pass

    def overall_grade(self):
        """
        Computes the weighted overall grade across all categories.

        Returns:
            float: The overall grade as a percentage (0-100).
        """
        pass

    def whatif_score(self, target_grade, future_weight):
        """
        Computes the score needed on a future assignment to reach a target grade.

        Args:
            target_grade (float): The desired final grade percentage (0-100).
            future_weight (float): The weight of the future assignment as a
                                   percentage of the total grade (0-100).

        Returns:
            dict: {
                'needed_score' (float): Score needed on the future assignment,
                'impossible' (bool): True if needed_score exceeds 100.
            }
        """
        pass


def compute_panic_score(current_score, exam_date_days_away, hours_studied, total_hours_needed=10):
    """
    Computes a panic score for an upcoming exam.

    panic_score = grade_risk x time_pressure x study_deficit x 100
    where:
        grade_risk     = (100 - current_score) / 100
        time_pressure  = 1 / max(days_away, 1)   (capped to avoid division by zero)
        study_deficit  = max(0, (total_hours_needed - hours_studied) / total_hours_needed)

    Args:
        current_score (float): Current grade in the relevant category (0-100).
        exam_date_days_away (int): Number of days until the exam. 0 is treated as 1
                                   to avoid division by zero.
        hours_studied (float): Hours already studied for the exam.
        total_hours_needed (float): Estimated total hours needed to be prepared.
                                    Default is 10.

    Returns:
        float: Panic score between 0 and 100 (higher = more urgent).
    """
    pass


def rank_exams(exams):
    """
    Ranks a list of exams by their panic score in descending order.

    Args:
        exams (list of dict): Each dict has keys:
                              'name' (str), 'current_score' (float),
                              'days_away' (int), 'hours_studied' (float)

    Returns:
        list of dict: Same exams sorted by panic_score descending,
                      each dict has an added 'panic_score' (float) key.
    """
    pass
