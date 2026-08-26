from dataclasses import dataclass
@dataclass(frozen=True)
class OperationalState:
    real_money_configured:bool=False
    economic_gate_passed:bool=False
    kill_switch:bool=False

def real_money_allowed(state:OperationalState)->bool:
    return False

def health_state(*,collector_ok,pit_ok,ledger_ok,kill_switch=False):
    return {'collector':'UP' if collector_ok else 'DOWN','pit':'UP' if pit_ok else 'DOWN','ledger':'UP' if ledger_ok else 'DOWN','kill_switch':bool(kill_switch),'status':'SAFE' if collector_ok and pit_ok and ledger_ok and not kill_switch else 'DEGRADED'}
