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
    async def _sys_call_buy_object_desc(kernel, session, pars):
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
        return await AgoraCalls._get_offer_from_pars_desc(fdb,
                offers, pars['ad_desc'], t_id)


    @staticmethod
    async def _get_offer_from_pars_idx(fdb, offers, par_idx, t_id):
        if len(offers) <= par_idx:
            raise AdelphosCoreException(ECoreErrno.EINVALID_AD_INDEX,
                            f"This agora has only {len(offers)} ads.")
        offer_taken = offers[par_idx]
        offer_ob = await fdb.uri_read_str(t_id, offer_taken, must_lock = True)
        return offer_ob


    @staticmethod
    async def _get_offer_from_pars_desc(fdb, offers, par_desc, t_id):
        for offer in offers:
            offer_ob = await fdb.uri_read_str(t_id, offer,
                                              must_lock = True)
            desc = offer_ob().get_scalar('description')
            gCon.log(f"object has description {desc}")
            if re.search(par_desc, desc) is not None:
                gCon.log(f"found!")
                return offer_ob
        raise AdelphosCoreException(ECoreErrno.ENO_SUCH_OBJECT,
                    f"no object with description {par_desc} found")


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

        #gCon.log(f"The export chain is {chain_exports}")

        import_family = chain_imports[-2]
        gCon.log(f"This is the last family that wants to import {import_family().ob.fields}")
        balance = import_family().get_scalar('balance')
        price_in_agora = offer_ob().get_as_list('prices')[pars['uplevel']]
        gCon.log(f"The balance is {balance} price in agora is {price_in_agora}")
        balance -= price_in_agora

        if balance >= 0:
            return

        balance_abs = abs(balance)
        balance_db = tutils.abs_to_db(balance_abs)

        gCon.log(f"The new balance will be {balance} which is {balance_db}db")

        #if balance_db < import_family()


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


