from django.test import SimpleTestCase

from .services import manual_phase_balanced_group_sizes, manual_phase_exact_distributions


class ManualPhaseDistributionTests(SimpleTestCase):
    def labels_for(self, total):
        return {option["label"] for option in manual_phase_exact_distributions(total)}

    def test_exact_distributions_for_36_cover_requested_formats(self):
        labels = self.labels_for(36)

        self.assertIn("18 duelos de 2", labels)
        self.assertIn("12 trio(s) de 3", labels)
        self.assertIn("9 grupos de 4", labels)
        self.assertIn("6 grupos de 6", labels)
        self.assertIn("4 grupos de 9", labels)
        self.assertIn("3 grupos de 12", labels)
        self.assertIn("2 grupos de 18", labels)
        self.assertIn("1 campal de 36", labels)

    def test_exact_distributions_for_10_do_not_offer_trios(self):
        labels = self.labels_for(10)

        self.assertIn("5 duelos de 2", labels)
        self.assertIn("2 grupos de 5", labels)
        self.assertIn("1 campal de 10", labels)
        self.assertNotIn("3 trio(s) de 3", labels)

    def test_balanced_custom_distribution_for_17_in_4_groups(self):
        self.assertEqual(manual_phase_balanced_group_sizes(17, 4), [5, 4, 4, 4])
