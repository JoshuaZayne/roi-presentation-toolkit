"""Client Data Handler - Input validation and management"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import json
from pathlib import Path
from datetime import datetime


@dataclass
class ClientData:
    """Client prospect data for ROI analysis."""
    name: str
    company: str
    industry: str
    current_annual_cost: float
    efficiency_gain: float
    implementation_cost: float
    annual_license: float
    years: int = 3
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    notes: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    custom_assumptions: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "company": self.company,
            "industry": self.industry,
            "current_annual_cost": self.current_annual_cost,
            "efficiency_gain": self.efficiency_gain,
            "implementation_cost": self.implementation_cost,
            "annual_license": self.annual_license,
            "years": self.years,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "notes": self.notes,
            "created_at": self.created_at,
            "custom_assumptions": self.custom_assumptions,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ClientData":
        return cls(
            name=data.get("name", "Unknown"),
            company=data.get("company", "Unknown"),
            industry=data.get("industry", "general"),
            current_annual_cost=float(data.get("current_annual_cost", 0)),
            efficiency_gain=float(data.get("efficiency_gain", 0)),
            implementation_cost=float(data.get("implementation_cost", 0)),
            annual_license=float(data.get("annual_license", 0)),
            years=int(data.get("years", 3)),
            contact_name=data.get("contact_name"),
            contact_email=data.get("contact_email"),
            notes=data.get("notes"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            custom_assumptions=data.get("custom_assumptions", {}),
        )

    def get_roi_inputs(self) -> dict:
        """Get inputs formatted for ROI model."""
        return {
            "current_annual_cost": self.current_annual_cost,
            "efficiency_gain": self.efficiency_gain,
            "implementation_cost": self.implementation_cost,
            "annual_license": self.annual_license,
            "years": self.years,
        }


class ClientDataLoader:
    """Load and manage client prospect data."""

    VALID_INDUSTRIES = [
        "banking",
        "insurance",
        "asset_management",
        "payments",
        "healthcare",
        "manufacturing",
        "retail",
        "technology",
        "general",
    ]

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else None
        self.clients: Dict[str, ClientData] = {}
        if self.storage_path and self.storage_path.exists():
            self._load_from_file()

    def _load_from_file(self) -> None:
        """Load clients from JSON file."""
        if self.storage_path and self.storage_path.exists():
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                for client_data in data.get("clients", []):
                    client = ClientData.from_dict(client_data)
                    self.clients[client.name] = client

    def _save_to_file(self) -> None:
        """Save clients to JSON file."""
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w") as f:
                json.dump({
                    "clients": [c.to_dict() for c in self.clients.values()]
                }, f, indent=2)

    def add_client(self, data: ClientData) -> None:
        """Add or update a client."""
        self.clients[data.name] = data
        self._save_to_file()

    def get_client(self, name: str) -> Optional[ClientData]:
        """Get client by name."""
        return self.clients.get(name)

    def list_clients(self) -> List[str]:
        """List all client names."""
        return list(self.clients.keys())

    def delete_client(self, name: str) -> bool:
        """Delete a client."""
        if name in self.clients:
            del self.clients[name]
            self._save_to_file()
            return True
        return False

    def validate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize client inputs.

        Returns:
            Validated input dictionary
        """
        validated = {}

        # Current annual cost - must be positive
        current_cost = inputs.get("current_annual_cost", 0)
        validated["current_annual_cost"] = max(0, float(current_cost))

        # Efficiency gain - must be between 0 and 1
        efficiency = inputs.get("efficiency_gain", 0)
        validated["efficiency_gain"] = min(1.0, max(0, float(efficiency)))

        # Implementation cost - must be non-negative
        impl_cost = inputs.get("implementation_cost", 0)
        validated["implementation_cost"] = max(0, float(impl_cost))

        # Annual license - must be non-negative
        license_cost = inputs.get("annual_license", 0)
        validated["annual_license"] = max(0, float(license_cost))

        # Years - must be between 1 and 10
        years = inputs.get("years", 3)
        validated["years"] = max(1, min(10, int(years)))

        # Industry - must be valid
        industry = inputs.get("industry", "general")
        validated["industry"] = industry if industry in self.VALID_INDUSTRIES else "general"

        return validated

    def validate_all(self, inputs: Dict[str, Any]) -> tuple:
        """
        Validate inputs and return validation result with errors.

        Returns:
            Tuple of (is_valid, validated_inputs, errors)
        """
        errors = []
        validated = {}

        # Required fields
        required_fields = ["current_annual_cost", "efficiency_gain", "annual_license"]
        for field in required_fields:
            if field not in inputs or inputs[field] is None:
                errors.append(f"Missing required field: {field}")

        # Validate values
        try:
            validated = self.validate(inputs)
        except (ValueError, TypeError) as e:
            errors.append(f"Invalid value: {str(e)}")

        # Business logic validation
        if validated.get("current_annual_cost", 0) <= 0:
            errors.append("Current annual cost must be greater than 0")

        if validated.get("efficiency_gain", 0) <= 0:
            errors.append("Efficiency gain must be greater than 0")

        if validated.get("annual_license", 0) <= 0:
            errors.append("Annual license cost must be greater than 0")

        # Warning if efficiency seems too high
        if validated.get("efficiency_gain", 0) > 0.5:
            errors.append("Warning: Efficiency gain above 50% may be optimistic")

        is_valid = len([e for e in errors if not e.startswith("Warning")]) == 0

        return is_valid, validated, errors

    def create_from_interactive(self) -> ClientData:
        """Interactive client data creation (for CLI use)."""
        print("\n=== New Client ROI Analysis ===\n")

        name = input("Analysis name: ").strip() or "Unnamed"
        company = input("Company name: ").strip() or "Unknown"

        print(f"\nAvailable industries: {', '.join(self.VALID_INDUSTRIES)}")
        industry = input("Industry [general]: ").strip() or "general"

        current_cost = float(input("\nCurrent annual cost ($): ") or 0)
        efficiency = float(input("Expected efficiency gain (0.0-1.0): ") or 0.3)
        impl_cost = float(input("Implementation cost ($): ") or 0)
        license_cost = float(input("Annual license cost ($): ") or 0)
        years = int(input("Analysis period (years) [3]: ") or 3)

        return ClientData(
            name=name,
            company=company,
            industry=industry,
            current_annual_cost=current_cost,
            efficiency_gain=efficiency,
            implementation_cost=impl_cost,
            annual_license=license_cost,
            years=years,
        )
