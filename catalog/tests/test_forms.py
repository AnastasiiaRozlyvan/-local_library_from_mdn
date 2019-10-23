import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from catalog.forms import RenewBookModelForm

from catalog.models import Author


class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_of_authors = 13

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f"Christian {author_id}", last_name=f"Surname {author_id}"
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/catalog/authors/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("authors"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("authors"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/author_list.html")

    def test_pagination_is_ten(self):
        response = self.client.get(reverse("authors"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertTrue(len(response.context["author_list"]) == 10)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse("authors") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertTrue(len(response.context["author_list"]) == 3)


class RenewBookFormTest(TestCase):
    def test_renew_form_date_field_label(self):
        form = RenewBookModelForm()
        self.assertTrue(
            form.fields["due_back"].label == None
            or form.fields["due_back"].label == "Renewal date"
        )

    def test_renew_form_date_field_help_text(self):
        form = RenewBookModelForm()
        self.assertEqual(
            form.fields["due_back"].help_text,
            "Enter a date between now and 4 weeks (default 3).",
        )

    def test_renew_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = RenewBookModelForm(data={"due_back": date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_too_far_in_future(self):
        date = (
            datetime.date.today()
            + datetime.timedelta(weeks=4)
            + datetime.timedelta(days=1)
        )
        form = RenewBookModelForm(data={"due_back": date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_today(self):
        date = datetime.date.today()
        form = RenewBookModelForm(data={"due_back": date})
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        date = timezone.localtime() + datetime.timedelta(weeks=4)
        form = RenewBookModelForm(data={"due_back": date})
        self.assertTrue(form.is_valid())
