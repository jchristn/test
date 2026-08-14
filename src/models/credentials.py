from pydantic import BaseModel, EmailStr, constr
import json
from pathlib import Path

class CredentialSet(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

    @classmethod
    def from_file(cls, path: str) -> "CredentialSet":
        data = Path(path).read_text()
        return cls.parse_raw(data)

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        # Exclude password from debugging output
        d.pop("password", None)
        return d

    def __repr__(self) -> str:
        return f"<CredentialSet email={self.email}>"
