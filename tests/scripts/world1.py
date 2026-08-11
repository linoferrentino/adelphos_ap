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


world_1_yaml = """

    instances:
        -  name: ad1
           host: www.ad1.com
           root: ad1root
           password: ad1pass

        -  name: ad2
           host: www.ad2.com
           root: ad2root
           password: ad2pass

        -  name: ad3
           host: www.ad3.com
           root: ad3root
           password: ad3pass

"""


fixture_1_yaml = """

  ad1_setup:

    users:

      - bob
      - alice
      - tom
      - jane

    families:

      - name: fam_t1
        members: 
          bob:
           password: bob_ps
          alice:
           password: alice_ps
        boss: alice
        equity: 33.92
        currency: EUR
        trust: 115

      - name: fam_t2
        members: 
          tom:
           password: tom_ps
          jane:
           password: jane_ps
        boss: tom
        equity: 102.92
        currency: EUR
        trust: 150


  ad2_setup:

    families:
      - name: fam_t2
        members:
          john_al:
            actor: '@john@www.ad3.com'
            password: john_pass
          katy_al:
            actor: '@katy@www.ad3.com'
            password: katy_pass
        boss: john_al
        equity: 239.19
        currency: EUR
        trust: 250
   

  ad3_setup:

    users:
      - john
      - katy

    families:
      - name: fam_t3
        members: 
          john_a3:
            password: john_a3pp
          katy_a3:
            password: katy_a3pp
        boss: john_a3
        equity: 63.44
        currency: USD 
        trust: 99


"""


