"""
DocumentStore — simulates a file storage system for documents.

Tools:
  - list_doc (READ): list all documents
  - retrieve_doc (READ): retrieve a document by name
  - search_doc (READ): search documents by keyword in name or content
  - add_doc (WRITE): add a new document
  - update_doc (WRITE): update an existing document's content
  - delete_doc (WRITE): delete a document
  - generate_invoice (WRITE): generate an invoice document
  - generate_report (WRITE): generate a report from multiple documents
"""

from runtime.apps.app import App, tool


class DocumentStore(App):

    def __init__(self):
        super().__init__()
        self.documents = {}

    @classmethod
    def from_config(cls, initial_state):
        instance = cls()
        for doc in initial_state.get("documents", []):
            instance.documents[doc["name"]] = doc["content"]
        return instance

    @tool()
    def list_doc(self) -> str:
        """List all documents in the store. Returns document names and a preview of their content.
        Returns:
            A formatted list of all document names with content previews.
        """
        if not self.documents:
            return "Document store is empty."
        lines = []
        for name, content in self.documents.items():
            preview = content[:80] + "..." if len(content) > 80 else content
            lines.append(f"  - {name}  |  {preview}")
        return f"Documents ({len(self.documents)}):\n" + "\n".join(lines)

    @tool()
    def retrieve_doc(self, name: str) -> str:
        """Retrieve a document from the store by its exact filename.
        Args:
            name: The exact filename to retrieve (e.g. 'timesheet_october.csv').
        Returns:
            The full document content, or an error message if not found.
        """
        if name not in self.documents:
            available = ", ".join(self.documents.keys())
            return f"Document '{name}' not found. Available documents: {available}"
        return f"Document '{name}':\n{self.documents[name]}"

    @tool()
    def search_doc(self, keyword: str) -> str:
        """Search documents by keyword. Matches against filenames and content (case-insensitive).
        Args:
            keyword: The search term to look for.
        Returns:
            List of matching document names, or a message if none found.
        """
        results = []
        for name, content in self.documents.items():
            if keyword.lower() in name.lower() or keyword.lower() in content.lower():
                results.append(name)
        if not results:
            return f"No documents matching '{keyword}'."
        return f"Documents matching '{keyword}':\n" + "\n".join(f"  - {r}" for r in results)

    @tool()
    def add_doc(self, name: str, content: str) -> str:
        """Add a new document to the store. Fails if a document with the same name exists.
        Args:
            name: The filename for the new document.
            content: The document content.
        Returns:
            Confirmation message with the document name.
        """
        if name in self.documents:
            return f"Document '{name}' already exists. Use update_doc to modify it."
        self.documents[name] = content
        return f"Document '{name}' added to store."

    @tool()
    def update_doc(self, name: str, content: str) -> str:
        """Update the content of an existing document.
        Args:
            name: The filename of the document to update.
            content: The new content to replace the existing content.
        Returns:
            Confirmation message, or error if document not found.
        """
        if name not in self.documents:
            return f"Document '{name}' not found. Use add_doc to create it."
        self.documents[name] = content
        return f"Document '{name}' updated."

    @tool()
    def delete_doc(self, name: str) -> str:
        """Delete a document from the store by its filename.
        Args:
            name: The filename of the document to delete.
        Returns:
            Confirmation of deletion, or error if not found.
        """
        if name not in self.documents:
            return f"Document '{name}' not found."
        del self.documents[name]
        return f"Document '{name}' deleted."

    @tool()
    def generate_invoice(self, client: str, items: str, total: str) -> str:
        """Generate an invoice document for a client.
        Args:
            client: The client name for the invoice.
            items: Line items description (e.g. 'Consulting 160h, Development 80h').
            total: The total amount (e.g. '45000.00 EUR').
        Returns:
            Confirmation that the invoice was created with its filename.
        """
        content = (
            f"INVOICE\n"
            f"{'='*40}\n"
            f"Client: {client}\n"
            f"Date: 2024-10-15\n\n"
            f"Items:\n{items}\n\n"
            f"Total: {total}\n"
            f"{'='*40}\n"
            f"Payment terms: Net 30"
        )
        filename = f"invoice_{client.lower().replace(' ', '_')}.pdf"
        self.documents[filename] = content
        return f"Invoice created: '{filename}' for {client}, total {total}."

    @tool()
    def generate_report(self, title: str, summary: str) -> str:
        """Generate a report document from a summary.
        Args:
            title: The report title.
            summary: The report content/summary text.
        Returns:
            Confirmation that the report was created with its filename.
        """
        content = (
            f"REPORT: {title}\n"
            f"{'='*40}\n"
            f"Generated: 2024-10-15\n\n"
            f"{summary}\n"
        )
        filename = f"report_{title.lower().replace(' ', '_')}.pdf"
        self.documents[filename] = content
        return f"Report created: '{filename}'."