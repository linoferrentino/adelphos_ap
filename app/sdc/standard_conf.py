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


adelphos_standard_configuration = {

        'modules' : [  {
                    'name' : Dependencies.ROUTER,
                    'constructor' : 'app.AdelphosRouter.AdelphosRouter',
                },
                {
                    'name' : Dependencies.CLI_HANDLER,
                    'constructor' : 'app.cli.StandardCliProvider.StandardCliProvider',
                },
                {
                    'name' : Dependencies.SOCIAL,
                    'constructor' : 'app.federation.BaseSocial.BaseSocial',
                },
                {
                    'name' : Dependencies.SOCIAL_NET,
                    'constructor' : 'app.federation.ap.ActivityPubNetwork.ActivityPubNetwork',
                },
                {
                    'name' : Dependencies.CLI_NET,
                    'constructor' : 'app.cli.AdelphosCliRouter.AdelphosCliRouter',
                },
                {
                    'name' : Dependencies.SOCIAL_DAO,
                    'constructor' : 'app.federation.store.SqliteSocialDao.SqliteSocialDao',
                },
                {
                    'name' : Dependencies.SOCIAL_GATEWAY,
                    'constructor' : 'app.federation.ap.ActivityPubGateway.ActivityPubGateway',
                },
                {
                    'name' : Dependencies.SOCIAL_API,
                    'constructor' : 'app.ad_api.adelphos.AdelphosApiProvider.AdelphosApiProvider',
                },
                {
                    'name' : Dependencies.RPC_API,
                    'constructor' : 'app.core.sys.SysCallGateway.SysCallGateway',
                    'args' : [ 'rpc_providers' ],
                },
                {
                    'name' : Dependencies.INBOX_API,
                    'constructor' : 'app.core.sys.SysCallGateway.SysCallGateway',
                    'args' : [ 'inbox_providers' ],
                },
                {
                    'name' : Dependencies.CLI_API,
                    'constructor' : 'app.core.sys.SysCallGateway.SysCallGateway',
                    'args' : [ 'cli_providers' ],
                },
        ],


}


adelphos_standard_configuration_deprecated = {
       'cli_handler' : {
                'type' : 'standard_cli',
                },
       'kernel': {
                'type' : 'adelphos',
            },
       'social': {
           'type' : 'activity_pub',
            },
       'social_api' : {
           'type' : 'adelphos',
           },
        'social_gateway' : {
           'type' : 'activity_pub',
           },
        'social_dao' : {
           'type' : 'sqlite',
            },
        }


