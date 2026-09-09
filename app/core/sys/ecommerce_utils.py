######################################################
#
# Adelphos AP: the fractal trust network
#
# Activity Pub implementation
#
# © 2025-26 Lino Ferrentino
# lino.ferrentino@gmail.com
#
# This is free software. Licensed with GPL version 3
#
######################################################


from app.sdc.Dependencies import Dependencies
from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.ECoreErrno import ECoreErrno
import app.misc.trust_utils as tutils
from app.logging import gCon


async def validate_balance_in_family(family_ob, new_balance, t_id):
    if new_balance == 0:
        return
    elif new_balance > 0:
        new_balance_db = tutils.abs_to_db(new_balance)
        my_trust = await family_ob().get_scalar('my_trust', t_id)
        if my_trust >= new_balance_db:
            return
        max_balance = tutils.db_to_abs(my_trust)
        raise AdelphosCoreException(
            ECoreErrno.EINSUFFICIENT_TRUST_IN_ADELPHOS,
         f"""Transaction aborted.
The family {family_ob().uri.name} cannot sell, it has
insuffient trust in the system.
Its new balance would be {new_balance} but its trust allows
it only to have a positive balance of {max_balance}""")
    else:
        new_balance_db = tutils.abs_to_db(abs(new_balance))
        system_trust = await family_ob().get_scalar('system_trust', t_id)
        if system_trust >= new_balance_db:
            return
        max_balance = tutils.db_to_abs(system_trust)

        raise AdelphosCoreException(
            ECoreErrno.EINSUFFICIENT_TRUST_FROM_ADELPHOS,
         f"""Transaction aborted.
The family {family_ob().uri.name} cannot buy, the system
has not sufficient trust in it.
Its new balance would be {new_balance} but its trust allows
it only to have a negative balance of -{max_balance}""")


async def get_total_tax_up(chain_exports, t_id):
    total_tax = 1.0
    for family in chain_exports[:-1]:
        family_tax = await family().get_scalar('import_export_tax', t_id)
        total_tax *= family_tax
    return total_tax


async def get_total_tax_chain_str(kernel, chain, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    total_tax = 1.0
    for family_str in chain:
        family_ob = await fdb.uri_read_str(t_id, family_str,
                    must_lock = True)
        family_tax = await family_ob().get_scalar('import_export_tax', t_id)
        total_tax *= family_tax
    return total_tax


async def distribuite_hearts_to_exports(kernel, hearts_given, chain_exports,
                                        t_id):

    await _distribute_hearts_to_chain(kernel, hearts_given, chain_exports,
                            'system_trust', t_id)


async def _distribute_hearts_to_chain(kernel, hearts_given,
                                      chain, trust_field, t_id):
    db_delta = -0.03 + ( 0.01 * hearts_given)
    gCon.log(f"Giving {db_delta} of trust {trust_field} to chain")

    for export_family in reversed(chain[:-1]):
        old_trust = await export_family().get_scalar(trust_field, t_id)
        new_trust = old_trust + db_delta
        export_family().set_scalar(trust_field, new_trust)


async def distribuite_hearts_to_imports(kernel, hearts_given, chain_imports,
                                        t_id):
    await _distribute_hearts_to_chain(kernel, hearts_given, chain_imports,
                            'my_trust', t_id)


async def distribuite_gains_to_exports(kernel, price, chain_exports, t_id):
    export_family = chain_exports[-2]
    balance = await export_family().get_scalar('balance', t_id)
    balance += price
    await validate_balance_in_family(export_family, balance, t_id)
    export_family().set_scalar('balance', balance)
    gCon.log(f"The family {export_family().uri.name} has a new balance {balance}")

    if len(chain_exports) == 2:
        return
 
    raise Exception("TODO")


async def distribuite_losses_to_imports(kernel, price, chain_imports, t_id):
    import_family = chain_imports[-2]
    balance = await import_family().get_scalar('balance', t_id)
    balance -= price
    await validate_balance_in_family(import_family, balance, t_id)
    import_family().set_scalar('balance', balance)

    gCon.log(f"The family {import_family().uri.name} has a new balance {balance}")

    if len(chain_imports) == 2:
        return

    raise Exception("TODO")
 

