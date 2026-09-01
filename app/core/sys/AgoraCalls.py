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

import re

from app.core.algo.utils import federated_transaction
from app.logging import gCon
from app.api.UserSession import active_login
from app.sdc.Dependencies import Dependencies
from app.core.ECoreErrno import ECoreErrno
from app.core.AdelphosCoreException import AdelphosCoreException

import app.core.sys.sys_calls_utils as scu
import app.core.sys.family_utils as fu
import app.misc.trust_utils as tutils
import app.core.sys.ecommerce_utils as ecut
import app.core.sys.task_utils as tku
import app.core.sys.agora_utils as au


class AgoraCalls:

    @staticmethod
    @active_login
    async def _sys_call_list_ads(kernel, session, pars):
        pars['_session'] = session
        return await AgoraCalls._agora_list_ads_safe(kernel, pars)
 

    @staticmethod
    @active_login
    async def _sys_call_buy_object_idx(kernel, session, pars):
        pars['_session'] = session
        return await AgoraCalls._agora_buy_object_safe(kernel, pars)


    @staticmethod
    @active_login
    async def _sys_call_buy_object_title(kernel, session, pars):
        pars['_session'] = session
        return await AgoraCalls._agora_buy_object_safe(kernel, pars)


    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def _agora_list_ads_safe(kernel, pars, t_id):
        return await AgoraCalls._agora_list_ads_impl(kernel, pars, t_id)


    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def _agora_buy_object_safe(kernel, pars, t_id):
        return await AgoraCalls._agora_buy_object_impl(kernel, pars, t_id)


    @staticmethod
    async def _get_offer_from_pars(fdb, offers, pars, t_id):
        if pars.get('index_ad') is not None:
            return await AgoraCalls._get_offer_from_pars_idx(fdb,
                    offers, pars['index_ad'], t_id)
        return await AgoraCalls._get_offer_from_pars_title(fdb,
                offers, pars['ad_title'], t_id)


    @staticmethod
    async def _get_offer_from_pars_idx(fdb, offers, par_idx, t_id):
        if len(offers) <= par_idx:
            raise AdelphosCoreException(ECoreErrno.EINVALID_AD_INDEX,
                            f"This agora has only {len(offers)} ads.")
        offer_taken = offers[par_idx]
        offer_ob = await fdb.uri_read_str(t_id, offer_taken, must_lock = True)
        return offer_ob


    @staticmethod
    async def _get_offer_from_pars_title(fdb, offers, par_title, t_id):
        for offer in offers:
            offer_ob = await fdb.uri_read_str(t_id, offer,
                                              must_lock = True)
            title = offer_ob().get_scalar('title')
            gCon.log(f"object has title {title}")
            if re.search(par_title, title) is not None:
                gCon.log(f"found!")
                return offer_ob
        raise AdelphosCoreException(ECoreErrno.ENO_SUCH_OBJECT,
                    f"no object with title {par_title} found")


    @staticmethod
    async def _agora_buy_object_impl(kernel, pars, t_id):
        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
        chain_imports = await scu.get_family_chain_up(kernel, pars, t_id)

        if len(chain_imports) < 2:
            raise AdelphosCoreException(ECoreErrno.ECANNOT_BUY_IN_YOUR_FAMILY,
                        "You cannot buy in your family")

        family_lev_ob = chain_imports[-1] 

        agora_ob = await fu.family_get_your_agora(kernel, family_lev_ob, t_id)
        offers = agora_ob().get_as_list('offers')

        offer_ob = await AgoraCalls._get_offer_from_pars(fdb, offers,
                                pars, t_id)

        if offer_ob().get_scalar('family_src') == chain_imports[0]().uri.unparse():
            raise AdelphosCoreException(ECoreErrno.ECANNOT_BUY_IN_YOUR_FAMILY,
                       f"The object {offer_ob().get_scalar('description')} is originated by your family.")

        chain_exports = await scu.get_family_chain_up_from_to(kernel,
                    offer_ob().get_scalar('family_src'), family_lev_ob, t_id)
        if len(chain_exports) != len(chain_imports):
            raise Exception("This version of adelphos handles symmetric chains: internal error")

        global_export_tax = ecut.get_total_tax_up(chain_exports)
        gCon.log(f"The export tax total is {global_export_tax}")

        price = offer_ob().get_scalar('price')
        agora_exported_price = price * global_export_tax
        gCon.log(f"The object price is {price} in agora is {agora_exported_price}")

        ecut.distribuite_losses_to_imports(kernel, agora_exported_price,
                                           chain_imports, t_id)

        ecut.distribuite_gains_to_exports(kernel, agora_exported_price,
                                          chain_exports, t_id)

        family_originator = chain_exports[0]
        agora_origin = await fu.family_get_your_agora(kernel, family_originator,
                                                      t_id)
        agora_origin().add_link('export_box', offer_ob)

        family_originator_boss = await fu.family_get_your_boss(kernel,
                    family_originator, t_id)

        await tku.add_task_to_alias(kernel, family_originator_boss,
                        'export_item', pars, t_id)

        await au.remove_object_from_export_chain(kernel, chain_exports,
                    offer_ob, t_id)


    @staticmethod
    async def _agora_list_ads_impl(kernel, pars, t_id):
        family_lev_ob = await scu.get_family_uplevel(kernel, pars, t_id)
        agora_uri = family_lev_ob().get_scalar('agora')
        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
        agora_ob = await fdb.uri_read_str(t_id, agora_uri, must_lock = True)
        offers = agora_ob().get_as_list('offers')
        if pars['get_only_uri'] == True:
            return offers

        ob_offers = []
        for offer in offers:
            offer_ob = await fdb.uri_read_str(t_id, offer,
                                              must_lock = False)
            ob_offers.append(offer_ob().ob.fields)

        return ob_offers


