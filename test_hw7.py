import unittest
import hw7


class TestCourse(unittest.TestCase):

    def test_add_category_stored_correctly(self):
        course = hw7.Course("CS515")
        course.add_category("Homework", 30, [80, 90, 70], drop_lowest=False)
        self.assertEqual(len(course.categories), 1)
        self.assertEqual(course.categories[0]['name'], "Homework")
        self.assertEqual(course.categories[0]['weight'], 30)
        self.assertEqual(course.categories[0]['scores'], [80, 90, 70])
        self.assertFalse(course.categories[0]['drop_lowest'])

    def test_add_multiple_categories(self):
        course = hw7.Course("CS515")
        course.add_category("Homework", 40, [85, 90])
        course.add_category("Final", 60, [75])
        self.assertEqual(len(course.categories), 2)

    def test_validate_weights_true(self):
        course = hw7.Course("CS515")
        course.add_category("Homework", 40, [80])
        course.add_category("Midterm", 30, [70])
        course.add_category("Final", 30, [90])
        self.assertTrue(course.validate_weights())

    def test_validate_weights_false(self):
        course = hw7.Course("CS515")
        course.add_category("Homework", 40, [80])
        course.add_category("Final", 50, [90])
        # weights sum to 90, not 100
        self.assertFalse(course.validate_weights())


class TestGradeCalculator(unittest.TestCase):

    def test_category_average_no_drop(self):
        # Build category dict directly — does not depend on add_category working
        category = {'name': 'Homework', 'weight': 100, 'scores': [80, 90, 100], 'drop_lowest': False}
        course = hw7.Course("CS515")
        calc = hw7.GradeCalculator(course)
        avg = calc.category_average(category)
        self.assertIsNotNone(avg)
        self.assertAlmostEqual(avg, 90.0, places=1)

    def test_category_average_with_drop_lowest(self):
        # HW1=50, HW2=90, HW3=88 → drop 50 → avg of 90 and 88 = 89
        category = {'name': 'Homework', 'weight': 100, 'scores': [50, 90, 88], 'drop_lowest': True}
        course = hw7.Course("CS515")
        calc = hw7.GradeCalculator(course)
        avg = calc.category_average(category)
        self.assertIsNotNone(avg)
        self.assertAlmostEqual(avg, 89.0, places=1)

    def test_category_average_empty_scores(self):
        category = {'name': 'Homework', 'weight': 100, 'scores': [], 'drop_lowest': False}
        course = hw7.Course("CS515")
        calc = hw7.GradeCalculator(course)
        avg = calc.category_average(category)
        self.assertEqual(avg, 0.0)

    def test_overall_grade_weighted(self):
        # HW worth 50% with avg 80, Final worth 50% with avg 100 → overall = 90
        course = hw7.Course("CS515")
        course.add_category("Homework", 50, [80], drop_lowest=False)
        course.add_category("Final", 50, [100], drop_lowest=False)
        calc = hw7.GradeCalculator(course)
        result = calc.overall_grade()
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 90.0, places=1)

    def test_overall_grade_drop_lowest_included(self):
        # HW: [50, 90, 88] drop_lowest=True → avg=89, weight=100 → overall=89
        course = hw7.Course("CS515")
        course.add_category("Homework", 100, [50, 90, 88], drop_lowest=True)
        calc = hw7.GradeCalculator(course)
        result = calc.overall_grade()
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 89.0, places=1)

    def test_whatif_score_achievable(self):
        # Current grade 88% weighted at 70%, final worth 30%
        # needed = (90 - 0.70*88) / 0.30 = 94.67
        course = hw7.Course("CS515")
        course.add_category("Current", 70, [88], drop_lowest=False)
        calc = hw7.GradeCalculator(course)
        result = calc.whatif_score(target_grade=90, future_weight=30)
        self.assertIsNotNone(result)
        self.assertFalse(result['impossible'])
        self.assertAlmostEqual(result['needed_score'], 94.67, delta=0.1)

    def test_whatif_score_impossible(self):
        # Failing badly, target is 93% — impossible
        course = hw7.Course("CS515")
        course.add_category("Current", 70, [40], drop_lowest=False)
        calc = hw7.GradeCalculator(course)
        result = calc.whatif_score(target_grade=93, future_weight=30)
        self.assertIsNotNone(result)
        self.assertTrue(result['impossible'])
        self.assertGreater(result['needed_score'], 100)

    def test_whatif_score_already_at_target(self):
        # Current grade already 95%, target 90% — needed score should be ≤ 100
        course = hw7.Course("CS515")
        course.add_category("Current", 70, [95], drop_lowest=False)
        calc = hw7.GradeCalculator(course)
        result = calc.whatif_score(target_grade=90, future_weight=30)
        self.assertIsNotNone(result)
        self.assertFalse(result['impossible'])
        self.assertLessEqual(result['needed_score'], 100)


class TestPanicScore(unittest.TestCase):

    def test_high_panic_close_exam_no_study(self):
        score = hw7.compute_panic_score(
            current_score=50, exam_date_days_away=1, hours_studied=0
        )
        self.assertIsNotNone(score)
        self.assertGreater(score, 0)

    def test_low_panic_far_exam_well_studied(self):
        score = hw7.compute_panic_score(
            current_score=90, exam_date_days_away=30, hours_studied=10
        )
        self.assertIsNotNone(score)
        self.assertLess(score, 5)

    def test_close_exam_panics_more_than_far_exam(self):
        close = hw7.compute_panic_score(
            current_score=70, exam_date_days_away=1, hours_studied=0
        )
        far = hw7.compute_panic_score(
            current_score=70, exam_date_days_away=30, hours_studied=10
        )
        self.assertIsNotNone(close)
        self.assertIsNotNone(far)
        self.assertGreater(close, far)

    def test_days_away_zero_does_not_crash(self):
        # days_away=0 must not raise ZeroDivisionError
        try:
            score = hw7.compute_panic_score(
                current_score=60, exam_date_days_away=0, hours_studied=2
            )
            self.assertIsNotNone(score)
        except ZeroDivisionError:
            self.fail("compute_panic_score raised ZeroDivisionError for days_away=0")


class TestRankExams(unittest.TestCase):

    def test_ranked_descending_by_panic_score(self):
        exams = [
            {'name': 'Math', 'current_score': 70, 'days_away': 30, 'hours_studied': 10},
            {'name': 'CS',   'current_score': 50, 'days_away': 1,  'hours_studied': 0},
        ]
        ranked = hw7.rank_exams(exams)
        self.assertIsNotNone(ranked)
        # CS exam should rank first (higher panic)
        self.assertEqual(ranked[0]['name'], 'CS')
        self.assertEqual(ranked[1]['name'], 'Math')

    def test_ranked_exams_have_panic_score_key(self):
        exams = [
            {'name': 'Physics', 'current_score': 80, 'days_away': 5, 'hours_studied': 3},
        ]
        ranked = hw7.rank_exams(exams)
        self.assertIsNotNone(ranked)
        self.assertIn('panic_score', ranked[0])


if __name__ == "__main__":
    unittest.main()
