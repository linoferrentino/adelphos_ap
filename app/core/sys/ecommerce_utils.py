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


async def distribute_gains_to_exports(kernel, price, chain_exports, t_id):

    await _distribute_delta_to_chain(kernel, price, chain_exports, t_id)


async def _distribute_delta_to_chain(kernel, delta, family_chain, t_id):

    exp_imp = "export" if delta > 0 else "import"

    top_family = family_chain[-2]
    await _change_family_balance(top_family, delta, t_id)

    if len(family_chain) == 2:
        return
 
    containing_family = family_chain[-2]
    inner_family = family_chain[-3]

    containing_family_uri = containing_family().uri.unparse()
    tax_rate = await inner_family().get_scalar('import_export_tax', t_id)
    tax_amount = abs(tax_rate * delta)
    gCon.log(f"the {exp_imp} family {containing_family_uri} has a tax gain of {tax_amount}")
    await _change_family_balance(containing_family, tax_amount, t_id)

    delta = delta - tax_amount
    gCon.log(f"The new delta is {delta}")

    brotherhood_ratio = await inner_family().get_scalar('brotherhood_ratio', t_id)
    uri_family = inner_family().uri.unparse()
    gCon.log(f"Distributing {delta} to uri {uri_family} from {containing_family_uri} using the members")

    members_list = await containing_family().get_as_object_list(
            'members', t_id)
    count_members = len(members_list)
    
    balance_to_members = (delta * brotherhood_ratio)
    balance_to_member = balance_to_members / (count_members - 1)
    balance_to_tx_family = delta - balance_to_members

    gCon.log(f"This family has {count_members} members who will take {balance_to_member} from the price each")
    gCon.log(f"The transaction family will take {balance_to_tx_family}")

    for member in members_list:
        if member ==  inner_family:
            gCon.log(f"this is the {exp_imp} family {member().uri.unparse()}")
            family_chain = family_chain[:-1]
            await _distribute_delta_to_chain(member,
                            balance_to_tx_family, chain_imports, t_id)
        else:
            gCon.log(f"this is another family {member().uri.unparse()}")
            await _change_family_balance(member, balance_to_member, t_id)


async def _change_family_balance(family, delta_balance, t_id):
    balance = await family().get_scalar('balance', t_id)
    balance += delta_balance 
    await validate_balance_in_family(family, balance, t_id)
    family().set_scalar('balance', balance)
    gCon.log(f"The family {family().uri.name} has a new balance {balance}")


async def distribute_losses_to_imports(kernel, price, chain_imports, t_id):
    import_family = chain_imports[-2]
    await _change_family_balance(import_family, -1 * price, t_id)

    if len(chain_imports) == 2:
        return

    containing_family = chain_imports[-2]

    for importing_family in reversed(chain_imports[:-2]):
        containing_family_uri = containing_family().uri.unparse()
        tax = await containing_family().get_scalar('import_export_tax', t_id)
        brotherhood_ratio = await containing_family().get_scalar('brotherhood_ratio', t_id)
        new_price = price * tax
        gCon.log(f"the new price is {new_price} ratio {brotherhood_ratio}")
        uri_family = importing_family().uri.unparse()
        gCon.log(f"Distributing loss {new_price} to uri {uri_family} from {containing_family_uri} using the members")

        members_list = await containing_family().get_as_object_list(
                'members', t_id)
        count_members = len(members_list)
        
        balance_to_members = (new_price * brotherhood_ratio) / count_members
        balance_to_import_family = (price - balance_to_members)

        gCon.log(f"This family has {count_members} members who will take {balance_to_members} from the price each")
        gCon.log(f"The importing family will take {balance_to_import_family}")

        for member in members_list:
            if member == importing_family:
                gCon.log(f"this is the importing family {member().uri.unparse()}")
                chain_imports = chain_imports[:-1]
                await distribute_losses_to_imports(member,
                                balance_to_import_family, chain_imports, t_id)
            else:
                gCon.log(f"this is another family {member().uri.unparse()}")
                await _change_family_balance(member, -1 * balance_to_members,
                                             t_id)

        


