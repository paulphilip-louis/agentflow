"""
EmailApp — simulates an email inbox and outbox.

Tools:
  - list_inbox (READ): list all emails in the inbox
  - read_email (READ): read a specific email by id
  - send_email (WRITE): send an email to a recipient
  - reply_to_email (WRITE): reply to an existing email
  - search_emails (READ): search emails by keyword
  - delete_email (WRITE): delete an email by id
"""

from runtime.apps.app import App, tool
from uuid import uuid4


class EmailApp(App):

    def __init__(self):
        super().__init__()
        self.inbox = {}
        self.outbox = {}

    @classmethod
    def from_config(cls, initial_state):
        instance = cls()
        for email in initial_state.get("inbox", []):
            eid = email.get("id", str(uuid4())[:8])
            instance.inbox[eid] = {
                "id": eid,
                "from": email["from"],
                "subject": email["subject"],
                "body": email["body"],
                "date": email.get("date", "2024-10-01"),
                "read": email.get("read", False),
            }
        for email in initial_state.get("outbox", []):
            eid = email.get("id", str(uuid4())[:8])
            instance.outbox[eid] = {
                "id": eid,
                "to": email["to"],
                "subject": email["subject"],
                "body": email["body"],
                "date": email.get("date", "2024-10-01"),
            }
        return instance

    @tool()
    def list_inbox(self) -> str:
        """List all emails in the inbox. Returns a summary of each email with id, sender, subject, and date."""
        if not self.inbox:
            return "Inbox is empty."
        lines = []
        for eid, email in self.inbox.items():
            status = "unread" if not email["read"] else "read"
            lines.append(f"[{eid}] From: {email['from']} | Subject: {email['subject']} | Date: {email['date']} | {status}")
        return "\n".join(lines)

    @tool()
    def read_email(self, email_id: str) -> str:
        """Read the full content of a specific email by its ID.
        Args:
            email_id: The unique identifier of the email to read.
        Returns:
            The full email including sender, subject, date and body.
        """
        email = self.inbox.get(email_id)
        if not email:
            return f"Email '{email_id}' not found in inbox."
        email["read"] = True
        return (
            f"From: {email['from']}\n"
            f"Subject: {email['subject']}\n"
            f"Date: {email['date']}\n"
            f"---\n"
            f"{email['body']}"
        )

    @tool()
    def search_emails(self, keyword: str) -> str:
        """Search inbox emails by keyword. Matches against subject and body.
        Args:
            keyword: The search term to look for in email subjects and bodies.
        Returns:
            List of matching emails with their IDs and subjects.
        """
        results = []
        for eid, email in self.inbox.items():
            if keyword.lower() in email["subject"].lower() or keyword.lower() in email["body"].lower():
                results.append(f"[{eid}] From: {email['from']} | Subject: {email['subject']}")
        if not results:
            return f"No emails found matching '{keyword}'."
        return "\n".join(results)

    @tool()
    def send_email(self, to: str, subject: str, body: str) -> str:
        """Send a new email to a recipient.
        Args:
            to: The recipient's email address.
            subject: The email subject line.
            body: The email body content.
        Returns:
            Confirmation with the sent email's ID.
        """
        eid = str(uuid4())[:8]
        self.outbox[eid] = {
            "id": eid,
            "to": to,
            "subject": subject,
            "body": body,
            "date": "2024-10-15",
        }
        return f"Email sent to {to} with subject '{subject}'. ID: {eid}"

    @tool()
    def reply_to_email(self, email_id: str, body: str) -> str:
        """Reply to an existing email in the inbox.
        Args:
            email_id: The ID of the email to reply to.
            body: The reply body content.
        Returns:
            Confirmation with the reply email's ID.
        """
        original = self.inbox.get(email_id)
        if not original:
            return f"Email '{email_id}' not found. Cannot reply."
        eid = str(uuid4())[:8]
        self.outbox[eid] = {
            "id": eid,
            "to": original["from"],
            "subject": f"Re: {original['subject']}",
            "body": body,
            "date": "2024-10-15",
        }
        return f"Reply sent to {original['from']} for '{original['subject']}'. ID: {eid}"

    @tool()
    def delete_email(self, email_id: str) -> str:
        """Delete an email from the inbox by its ID.
        Args:
            email_id: The ID of the email to delete.
        Returns:
            Confirmation of deletion or error if not found.
        """
        if email_id in self.inbox:
            del self.inbox[email_id]
            return f"Email '{email_id}' deleted from inbox."
        return f"Email '{email_id}' not found in inbox."