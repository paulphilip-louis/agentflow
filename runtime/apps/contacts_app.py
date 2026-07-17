"""
ContactsApp — simulates an address book / CRM contacts list.

Tools:
  - list_contacts (READ): list all contacts
  - get_contact (READ): get a specific contact's details
  - search_contacts (READ): search contacts by name or company
  - add_contact (WRITE): add a new contact
  - update_contact (WRITE): update a contact's information
"""

from runtime.apps.app import App, tool
from uuid import uuid4


class ContactsApp(App):

    def __init__(self):
        super().__init__()
        self.contacts = {}

    @classmethod
    def from_config(cls, initial_state):
        instance = cls()
        for contact in initial_state.get("contacts", []):
            cid = contact.get("id", str(uuid4())[:8])
            instance.contacts[cid] = {
                "id": cid,
                "name": contact["name"],
                "email": contact.get("email", ""),
                "phone": contact.get("phone", ""),
                "company": contact.get("company", ""),
                "role": contact.get("role", ""),
                "notes": contact.get("notes", ""),
            }
        return instance

    @tool()
    def list_contacts(self) -> str:
        """List all contacts in the address book. Returns name, email, company and role for each contact."""
        if not self.contacts:
            return "No contacts found."
        lines = []
        for cid, c in self.contacts.items():
            lines.append(f"[{cid}] {c['name']} | {c['email']} | {c['company']} — {c['role']}")
        return "\n".join(lines)

    @tool()
    def get_contact(self, contact_id: str) -> str:
        """Get full details of a specific contact by ID.
        Args:
            contact_id: The unique identifier of the contact.
        Returns:
            All details including name, email, phone, company, role and notes.
        """
        c = self.contacts.get(contact_id)
        if not c:
            return f"Contact '{contact_id}' not found."
        return (
            f"Name: {c['name']}\n"
            f"Email: {c['email']}\n"
            f"Phone: {c['phone']}\n"
            f"Company: {c['company']}\n"
            f"Role: {c['role']}\n"
            f"Notes: {c['notes']}"
        )

    @tool()
    def search_contacts(self, query: str) -> str:
        """Search contacts by name or company. Case-insensitive partial match.
        Args:
            query: The search term to match against contact names and companies.
        Returns:
            List of matching contacts with their IDs and details.
        """
        results = []
        for cid, c in self.contacts.items():
            if query.lower() in c["name"].lower() or query.lower() in c["company"].lower():
                results.append(f"[{cid}] {c['name']} | {c['email']} | {c['company']}")
        if not results:
            return f"No contacts found matching '{query}'."
        return "\n".join(results)

    @tool()
    def add_contact(self, name: str, email: str = "", phone: str = "",
                    company: str = "", role: str = "", notes: str = "") -> str:
        """Add a new contact to the address book.
        Args:
            name: The contact's full name.
            email: Email address (optional).
            phone: Phone number (optional).
            company: Company name (optional).
            role: Job title or role (optional).
            notes: Additional notes (optional).
        Returns:
            Confirmation with the new contact's ID.
        """
        cid = str(uuid4())[:8]
        self.contacts[cid] = {
            "id": cid,
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "role": role,
            "notes": notes,
        }
        return f"Contact '{name}' added. ID: {cid}"

    @tool()
    def update_contact(self, contact_id: str, name: str = "", email: str = "",
                       phone: str = "", company: str = "", role: str = "", notes: str = "") -> str:
        """Update an existing contact's information. Only non-empty fields are updated.
        Args:
            contact_id: The ID of the contact to update.
            name: New name (leave empty to keep current).
            email: New email (leave empty to keep current).
            phone: New phone (leave empty to keep current).
            company: New company (leave empty to keep current).
            role: New role (leave empty to keep current).
            notes: New notes (leave empty to keep current).
        Returns:
            Confirmation of the update.
        """
        c = self.contacts.get(contact_id)
        if not c:
            return f"Contact '{contact_id}' not found."
        if name: c["name"] = name
        if email: c["email"] = email
        if phone: c["phone"] = phone
        if company: c["company"] = company
        if role: c["role"] = role
        if notes: c["notes"] = notes
        return f"Contact '{c['name']}' (ID: {contact_id}) updated."