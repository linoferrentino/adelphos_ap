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
#

# the logic to create an alias in the model.

#from app.dao.FamilyDao import FamilyDao
#from app.dao.AliasDao import AliasDao
#from app.core.EAdErrno import EAdErrno
#from app.core.FamilyModel import FamilyModel
#from app.core.AliasModel import AliasModel
#from app.core.BaseIdModel import AD_INVALID_ID
#from app.core.BaseModel import BaseModel
#from app.logging import gCon
#import traceback
from argon2 import PasswordHasher
#from app.core.AdelphosCoreException import AdelphosCoreException
#
#from app.core.algo.utils import commit_or_errno
#from app.core.algo.utils import commit_or_raise
from app.core.algo.utils import federated_transaction
from app.core.algo.FamilyAlgo import FamilyAlgo
from app.core.model.AliasFob import AliasFob
#from app.dao.AdelphosUri import uriparse_type
#from app.dao.AdelphosUri import EAdelphosType
#
#from app.core.AliasModel import alias_dto_password


class AliasAlgo:


    def __init__(self, kernel):
        self.kernel = kernel 


    #@commit_or_errno
    @federated_transaction(raise_if_fail = False)
    def alias_create(self, actor_id, name, family, password, t_id):
        #return self._alias_create_impl(actor_id, alias_name, alias_family, password_clear)

        ph = PasswordHasher()
        pass_hashed = ph.hash(password)

        fields = {
                'actor_id' : actor_id,
                'password': pass_hashed
        }

        fob1 = self.kernel.fdb.new_ob(t_id, AliasFob._type, name, family, fields = fields)

        return fob1
 


    # this can be called also externally to create the root alias
    #@commit_or_errno

    #    #return self._alias_create_internal_hashed(actor_id, alias_name,
    #    #                                          alias_family, pass_hashed)
    #    pass


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


   

    #def _alias_create_internal_hashed(self, actor_id, alias_name, alias_family, pass_hashed):


    #    #zioa 

    #    #fam_ob = self.instance.family_model.create(alias_family)
    #    #alias_ob = self.instance.alias_model.create(actor_id, alias_name, fam_ob, pass_hashed)

    #    #self.instance.family_model.set_boss(fam_ob, alias_ob)

    #    #return BaseModel.get_id(alias_ob)

    #    pass

