from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core import mail
from django.conf import settings
from unittest.mock import patch, MagicMock
from people.utils import send_password_reset_email


class UtilsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    @patch('people.utils.get_current_site')
    @patch('people.utils.send_mail')
    def test_send_password_reset_email_success(self, mock_send_mail, mock_get_current_site):
        
        mock_site = MagicMock()
        mock_site.domain = 'example.com'
        mock_get_current_site.return_value = mock_site

        
        request = self.factory.get('/test/')

        
        send_password_reset_email(self.user, request)

        
        mock_send_mail.assert_called_once()
        
        
        call_args = mock_send_mail.call_args
        subject, message, from_email, recipient_list = call_args[0]
        
        
        self.assertEqual(subject, "Password Reset Request")
        self.assertEqual(from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(recipient_list, [self.user.email])
        self.assertIn(self.user.username, message)
        self.assertIn('example.com', message)
        self.assertIn('reset-password-confirm', message)

    @patch('people.utils.get_current_site')
    @patch('people.utils.send_mail')
    def test_send_password_reset_email_with_different_domain(self, mock_send_mail, mock_get_current_site):
        
        mock_site = MagicMock()
        mock_site.domain = 'myschool.edu'
        mock_get_current_site.return_value = mock_site

        
        request = self.factory.get('/test/')

        
        send_password_reset_email(self.user, request)

        
        mock_send_mail.assert_called_once()
        
        
        call_args = mock_send_mail.call_args
        subject, message, from_email, recipient_list = call_args[0]
        
        
        self.assertIn('myschool.edu', message)

    @patch('people.utils.get_current_site')
    @patch('people.utils.send_mail')
    def test_send_password_reset_email_send_mail_failure(self, mock_send_mail, mock_get_current_site):
        
        mock_site = MagicMock()
        mock_site.domain = 'example.com'
        mock_get_current_site.return_value = mock_site

        
        mock_send_mail.side_effect = Exception("SMTP error")

        
        request = self.factory.get('/test/')

        
        with self.assertRaises(Exception):
            send_password_reset_email(self.user, request)

    @patch('people.utils.get_current_site')
    @patch('people.utils.send_mail')
    def test_send_password_reset_email_with_special_characters(self, mock_send_mail, mock_get_current_site):
        
        special_user = User.objects.create_user(
            username='test.user@domain',
            email='special@example.com',
            password='testpass123'
        )

        
        mock_site = MagicMock()
        mock_site.domain = 'example.com'
        mock_get_current_site.return_value = mock_site

        
        request = self.factory.get('/test/')

        
        send_password_reset_email(special_user, request)

        
        mock_send_mail.assert_called_once()
        
     
        call_args = mock_send_mail.call_args
        subject, message, from_email, recipient_list = call_args[0]
        
        
        self.assertIn(special_user.username, message)
        self.assertEqual(recipient_list, [special_user.email])

    @patch('people.utils.get_current_site')
    @patch('people.utils.send_mail')
    def test_send_password_reset_email_multiple_calls(self, mock_send_mail, mock_get_current_site):
        
        mock_site = MagicMock()
        mock_site.domain = 'example.com'
        mock_get_current_site.return_value = mock_site

        
        request = self.factory.get('/test/')

        
        send_password_reset_email(self.user, request)
        send_password_reset_email(self.user, request)

        
        self.assertEqual(mock_send_mail.call_count, 2)
        
        
        for call in mock_send_mail.call_args_list:
            subject, message, from_email, recipient_list = call[0]
            self.assertEqual(recipient_list, [self.user.email]) 