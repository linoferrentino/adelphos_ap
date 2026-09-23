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


from enum import StrEnum
from enum import auto

class EBMod(StrEnum):
    REAL = auto()
    PENDING = auto()
    CONFIRMED = auto()


async def validate_balance_in_family(family_ob, new_balance, t_id):
    family_uri = family_ob().uri.unparse()
    if new_balance == 0:
        return
    elif new_balance > 0:
        new_balance_db = tutils.abs_to_db(new_balance)
        my_trust = await family_ob().get_scalar('my_trust', t_id)
        if my_trust >= new_balance_db:
            gCon.log(f"{family_uri} new balance_db [green]{new_balance} = {new_balance_db}db[/green] my_trust [green]{my_trust}db[/green]")
            return
        max_balance = tutils.db_to_abs(my_trust)
        raise AdelphosCoreException(
            ECoreErrno.EINSUFFICIENT_TRUST_IN_ADELPHOS,
         f"""Transaction aborted.
The family {family_uri} cannot sell, it has
insuffient trust in the system.
Its new balance would be {new_balance} but its trust allows
it only to have a positive balance of {max_balance}""")
    else:
        new_balance_db = tutils.abs_to_db(abs(new_balance))
        system_trust = await family_ob().get_scalar('system_trust', t_id)
        if system_trust >= new_balance_db:
            gCon.log(f"{family_uri} new balance_db [red]{new_balance} = {new_balance_db}dB[/red] system_trust [red]{system_trust}db[/red]")
            return
        max_balance = tutils.db_to_abs(system_trust)

        raise AdelphosCoreException(
            ECoreErrno.EINSUFFICIENT_TRUST_FROM_ADELPHOS,
         f"""Transaction aborted.
The family {family_uri} cannot buy, the system
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


async def complete_buy_task(kernel, hearts_given,
                            exp_chain, imp_chain, t_id):

    await change_brotherhood(kernel, hearts_given, exp_chain, t_id)
    await distribuite_hearts_to_imports(kernel, hearts_given, exp_chain, t_id)
    await distribuite_hearts_to_exports(kernel, hearts_given, imp_chain, t_id)


async def change_brotherhood(kernel, hearts_given, chain, t_id):
    agora_family = chain[-1]
    old_brotherhood = await agora_family().get_scalar(
            'brotherhood_ratio', t_id)
    if hearts_given < 3:
        delta_brotherhood = (-0.01 * (3-hearts_given)) * old_brotherhood
    else:
        delta_brotherhood = (0.01 * (hearts_given-2)) * (1.0 - old_brotherhood)

    new_brotherhood = old_brotherhood + delta_brotherhood
    gCon.log(f"{agora_family().uri.unparse()} brotherhood {old_brotherhood} + {delta_brotherhood} = {new_brotherhood}")
    agora_family().set_scalar('brotherhood_ratio', new_brotherhood)


async def _distribute_hearts_to_chain(kernel, hearts_given,
                                      chain, trust_field, t_id):
    db_delta = -0.03 + ( 0.01 * hearts_given)
    gCon.rule(f"TRUST MOD: {db_delta} of trust {trust_field} to chain")

    for export_family in reversed(chain[:-1]):
        old_trust = await export_family().get_scalar(trust_field, t_id)
        new_trust = old_trust + db_delta
        gCon.log(f"{export_family().uri.name} {trust_field} from {old_trust} to {new_trust}")
        export_family().set_scalar(trust_field, new_trust)


async def distribuite_hearts_to_imports(kernel, hearts_given, chain_imports,
                                        t_id):
    await _distribute_hearts_to_chain(kernel, hearts_given, chain_imports,
                            'my_trust', t_id)


async def _distribute_gains_to_exports(kernel, price, chain_exports,
                                      bmod_type, t_id):
    gCon.log(f"[blue]================ start {bmod_type} gain distribution {price}[/blue]")
    await _distribute_delta_to_chain(kernel, price, chain_exports, bmod_type,
                                     t_id)
    gCon.log(f"[blue]================ end {bmod_type} gain distribution[/blue]")


async def _distribute_delta_to_chain(kernel, delta, family_chain, bmod_type,
                                     t_id):

    exp_imp = "export" if delta > 0 else "import"

    top_family = family_chain[-2]

    if len(family_chain) == 2:
        gCon.log("This is the ultimate family, it takes all the delta.")
        await _change_family_balance(top_family, delta, bmod_type, t_id)
        return
 
    containing_family = family_chain[-2]
    inner_family = family_chain[-3]

    containing_family_uri = containing_family().uri.unparse()
    gCon.log(f"This is a containing family {containing_family_uri}")
    tax_rate = await inner_family().get_scalar('import_export_tax', t_id)
    tax_amount = abs((tax_rate - 1) * delta)
    gCon.log(f"the {exp_imp} family {containing_family_uri} has a tax rate {tax_rate} delta {delta} gain of {tax_amount}")
    await _change_family_balance(containing_family, tax_amount, bmod_type,
                                 t_id)

    delta = delta - tax_amount
    gCon.log(f"The new delta is {delta}")

    brotherhood_ratio = await containing_family().get_scalar(
            'brotherhood_ratio', t_id)
    uri_family = inner_family().uri.unparse()
    gCon.log(f"Distributing {delta} to uri {uri_family} from {containing_family_uri} with ratio {brotherhood_ratio}")

    balance_to_family = (delta * brotherhood_ratio)
    balance_to_tx_family = delta - balance_to_family

    gCon.log(f"This family will take {balance_to_family} of the total transaction")
    gCon.log(f"The transaction family will take {balance_to_tx_family}")

    await _change_family_balance(containing_family, balance_to_family,
                                 bmod_type, t_id)
    family_chain = family_chain[:-1]
    await _distribute_delta_to_chain(inner_family, balance_to_tx_family,
                                     family_chain, bmod_type, t_id)


async def get_family_balance(family, t_id):

    pending_balance = await family().get_scalar('pending_balance', t_id)
    real_balance = await family().get_scalar('balance', t_id)
    return (real_balance, pending_balance,
            pending_balance + real_balance)


async def _change_family_balance(family, delta_balance, bmod_type, t_id):

    if delta_balance == 0.0:
        return

    (real_balance, pending_balance, total_balance) = await \
            get_family_balance(family, t_id)

    if bmod_type != EBMod.CONFIRMED:
        if ((delta_balance * pending_balance) <= 0):
            balance_to_check = real_balance + delta_balance
        else:
            balance_to_check = total_balance + delta_balance
        await validate_balance_in_family(family, balance_to_check, t_id)

    gCon.log(f"[yellow] change {bmod_type} balance for {family().uri.name} --> {real_balance} + {pending_balance} = {total_balance} delta {delta_balance} [/yellow]")

    match bmod_type:
        case EBMod.REAL:
            real_balance += delta_balance
        case EBMod.PENDING:
            pending_balance += delta_balance
        case EBMod.CONFIRMED:
            if delta_balance * pending_balance <= 0:
                real_balance += delta_balance
                pending_balance -= delta_balance
            else:
                if abs(pending_balance) > abs(delta_balance):
                    gCon.log("c3")
                    pending_balance -= delta_balance
                    real_balance += delta_balance
                else:
                    gCon.log("c4")
                    pending_balance = 0
                    real_balance += (delta_balance - pending_balance)

    new_balance = real_balance + pending_balance

    gCon.log(f"[yellow]AFTER {bmod_type} modify: {family().uri.name} --> {real_balance} + {pending_balance} = {new_balance} [/yellow]")

    if bmod_type == EBMod.CONFIRMED:
        assert (abs(total_balance - new_balance) < 1e-3)
    else:
        assert ((abs(total_balance - new_balance) - abs(delta_balance)) < 1e-3)
   
    family().set_scalar('pending_balance', pending_balance)
    family().set_scalar('balance', real_balance)


async def _distribute_losses_to_imports(kernel, price, chain_imports, bmod_type,
                                       t_id):
    gCon.log(f"[red]=================== start {bmod_type} loss distribution -{price}[/red]")
    await _distribute_delta_to_chain(kernel, price * (-1.0), 
                                     chain_imports, bmod_type, t_id)
    gCon.log(f"[red]==================== end {bmod_type} loss distribution[/red]")



async def distribute_losses_and_gains(kernel, price, chain_exports, chain_imports,
                                       bmod_type, t_id):

    await _distribute_losses_to_imports(kernel,
            price, chain_imports, bmod_type, t_id)

    await _distribute_gains_to_exports(kernel,
            price, chain_exports, bmod_type, t_id)

