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


from argon2 import PasswordHasher
from app.core.algo.utils import federated_transaction
from app.core.algo.FamilyAlgo import FamilyAlgo
from app.core.model.AdelphosUri import EAdelphosType
from app.logging import gCon
from app.core.ECoreErrno import ECoreErrno
from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.model.AdelphosUri import AdelphosUri
from app.sdc.Dependencies import Dependencies
import weakref
import sys
import app.misc.alias_utils as au


class AliasAlgo:


    @staticmethod
    async def _sys_call_create(kernel, envelope, pars):
        alias_name = pars['name']
        password = pars['password']

        (alias, family) = au.split_alias(alias_name, True)

        await AliasAlgo.alias_create_safe(kernel, envelope.actor_from.act.actor_id,
                                     alias, family, password)
        return "Alias created, you can login, now."


    @staticmethod
    @federated_transaction(raise_if_fail = False)
    async def alias_create(kernel, actor_id, name, family, password, t_id):
        return await AliasAlgo._alias_create_impl(kernel, actor_id, 
                                            name, family, password, t_id)
 

    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def alias_create_safe(kernel, actor_id, name, family, password, t_id):
        return await AliasAlgo._alias_create_impl(kernel, actor_id, 
                                            name, family, password, t_id)
 

    async def _alias_create_impl(kernel, actor_id, name, family, password, t_id):

        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
        family_uri = AdelphosUri(EAdelphosType.FAMILY_TYPE, family)

        is_present_family = await fdb.is_present_uri_str(t_id, family_uri)

        if is_present_family is True:
            raise AdelphosCoreException(ECoreErrno.EDUPLICATED_FAMILY)

        family_ob = await fdb.new_ob_uri(t_id, family_uri)
        family_ob().add_phantom_link()

        ph = PasswordHasher()
        pass_hashed = ph.hash(password)

        fields = {
                'actor_id' : actor_id,
                'password': pass_hashed
        }

        alias_ob = await fdb.new_ob(t_id, EAdelphosType.ALIAS_TYPE, 
                                      name, family = family, fields = fields)
 


    # it returns the id of the new alias.
    #def _alias_create_impl(self, actor_id, alias_name, alias_family, password_clear):

    #    #fam_ob = self.instance.family_model.open_name(alias_family, maybe = True)

    #    #if fam_ob is not None:
    #    #    gCon.log(f"fam ob {fam_ob}")
    #    #    raise AdelphosCoreException(EAdErrno.EDUPLICATED_FAMILY)

    #    #ph = PasswordHasher()
    #    #pass_hashed = ph.hash(password_clear)

    #    #aoao

    #    #return self._alias_create_internal_hashed(actor_id, alias_name,
    #    #                                          alias_family, pass_hashed)
    #    pass

    #@commit_or_raise
    #def login_or_die(self, name, family, password, force = False):
    #    #return self._login_impl(name, family, password, force)
    #    pass


    #@commit_or_errno
    #def login(self, name, family, password, force = False):
    #    #return self._login_impl(name, family, password, force)
    #    pass


    #def _login_impl(self,  name, family, password, force):

    #    #alias_ob = self.instance.alias_model.open_name_id_base(name, family)
    #    #if alias_ob == None:
    #    #    raise AdelphosCoreException(EAdErrno.EINVALID_USER_OR_PASSWORD,
    #    #                                   f"undefined alias {name}.{family}")

    #    #if force == True:
    #    #    return BaseIdModel.get_id(alias_ob)

    #    ## password check
    #    #ph = PasswordHasher()
    #    #try:
    #    #    res = ph.verify(alias_dto_password(alias_ob), password)
    #    #except:
    #    #    raise AdelphosCoreException(EAdErrno.EINVALID_USER_OR_PASSWORD,
    #    #                                f"infalid {password}")

    #    #return BaseModel.get_id(alias_ob)
    #    pass


   

    
