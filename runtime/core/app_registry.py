"""
App Registry — maps YAML app names to their Python classes.
 
Add new apps here when you create them.
"""

from runtime.apps.document_store import DocumentStore
from runtime.apps.email_app import EmailApp
from runtime.apps.calendar_app import CalendarApp
from runtime.apps.contacts_app import ContactsApp

APP_REGISTRY = {
    "document_store": DocumentStore,
    "email": EmailApp,
    "calendar": CalendarApp,
    "contacts": ContactsApp,
}