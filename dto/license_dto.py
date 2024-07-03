from dataclasses import dataclass

@dataclass
class LicenseDTO:
    userId: str
    validity: str
    licenseKey: str
    type: str
    trader: str
    
    @classmethod
    def from_json(cls, json):
        return cls(**json)