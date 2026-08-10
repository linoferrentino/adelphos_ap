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
    levels: 0
    users:
      - bob
      - alice
    level_0:
      - name: fam_t1
        members: 
          - alias: bob
          - alias: alice
        equity: 33.92
        currency: EUR

  ad2_setup:
    levels: 0
    level_0:
      - name: fam_t2
        members:
          - alias: john_al
            actor: '@john@www.ad3.com'
          - alias: katy_al
            actor: '@katy@www.ad3.com'
        equity: 239.19
        currency: EUR
   

  ad3_setup:
    levels: 0
    users:
      - john
      - katy
    level_0:
      - name: fam_t3
        members: 
          - alias: john_a3
          - alias: katy_a3
        equity: 63.44
        currency: USD 


"""


