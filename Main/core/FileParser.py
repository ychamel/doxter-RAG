import json
from io import BytesIO
from typing import List, Any, Optional

from langchain.docstore.document import Document
from langchain.load import dumps, loads


from abc import ABC
from copy import deepcopy


class File(ABC):
    """Represents an uploaded file comprised of Documents"""

    def __init__(
            self,
            name: str,
            id: str,
            metadata: Optional[dict[str, Any]] = None,
            docs: Optional[List[Document]] = None,
    ):
        self.name = name
        self.id = id
        self.metadata = metadata or {}
        self.docs = docs or []

    @classmethod
    def from_bytes(cls, file: BytesIO) -> "File":
        """Creates a File from a BytesIO object"""
        return None

    @classmethod
    def from_url(cls, url: str) -> "File":
        """Creates a File from a BytesIO object"""
        return None

    def __repr__(self) -> str:
        return (
            f"File(name={self.name}, id={self.id},"
            " metadata={self.metadata}, docs={self.docs})"
        )

    def __str__(self) -> str:
        return f"File(name={self.name}, id={self.id}, metadata={self.metadata})"

    def copy(self) -> "File":
        """Create a deep copy of this File"""
        return self.__class__(
            name=self.name,
            id=self.id,
            metadata=deepcopy(self.metadata),
            docs=deepcopy(self.docs),
        )

    def json(self):
        docs = []
        for doc in self.docs:
            docs.append(dumps(doc))

        parsed_file = {
            "name": self.name,
            "id": self.id,
            "metadata": self.metadata,
            "docs": docs,
        }
        return json.dumps(parsed_file)

    @staticmethod
    def load(json_file):
        parsed_file = json.loads(json_file)
        name = parsed_file.get("name")
        id = parsed_file.get("id")
        metadata = parsed_file.get("metadata")
        parsed_docs = parsed_file.get("docs")
        docs = []
        for doc in parsed_docs:
            docs.append(loads(doc))

        return File(name=name,
                    id=id,
                    metadata=metadata,
                    docs=docs)

