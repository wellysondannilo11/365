# SOURCE CONFLICT ENGINE

Implementado no `ml/app/master_staff/source_conflict.py`.

## Regras
- `CONSENSUS`: todas as fontes materializadas concordam.
- `MINOR_CONFLICT`: duas representações diferentes; a feature fica bloqueada.
- `MAJOR_CONFLICT`: múltiplos valores divergentes; a feature fica bloqueada.
- `UNVERIFIED`: não há evidência suficiente; bloqueada.
- `LEAKAGE`: qualquer fonte tem timestamp posterior ao `decision_timestamp`; bloqueada.

Nenhuma fonte é escolhida silenciosamente. A divergência e os timestamps são preservados.
