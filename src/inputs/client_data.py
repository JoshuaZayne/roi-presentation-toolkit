"""Client Data Handler"""
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ClientData:
    name: str
    current_annual_cost: float
    efficiency_gain: float
    implementation_cost: float
    annual_license: float
    years: int = 3

class ClientDataLoader:
    def __init__(self):
        self.clients = {}

    def add_client(self, data: ClientData) -> None:
        self.clients[data.name] = data

    def get_client(self, name: str) -> Optional[ClientData]:
        return self.clients.get(name)

    def validate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'current_annual_cost': max(0, float(inputs.get('current_annual_cost', 0))),
            'efficiency_gain': min(1.0, max(0, float(inputs.get('efficiency_gain', 0)))),
            'implementation_cost': max(0, float(inputs.get('implementation_cost', 0))),
            'annual_license': max(0, float(inputs.get('annual_license', 0))),
            'years': max(1, min(10, int(inputs.get('years', 3))))
        }
