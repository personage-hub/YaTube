from http import HTTPStatus

from django.test import Client, TestCase

URL_AUTHOR = '/about/author/'
URL_TECH = '/about/tech/'


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности статичных адресов."""
        urls = [URL_AUTHOR, URL_AUTHOR]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов для статичных адресов."""
        template_url = {
            'about/author.html': URL_AUTHOR,
            'about/tech.html': URL_TECH
        }
        for template, url in template_url.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
