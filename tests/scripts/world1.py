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


basic_ad1_setup_yaml = """

  ad1_setup:

    users:

      - bob
      - alice
      - tom
      - jane
      - bill
      - pat

    families:

      - name: fam_t1
        members: 
          bob:
           password: bob_ps
          alice:
           password: alice_ps
        boss: alice
        balance: 33.92
        my_trust: 115
        location: fam_t1_loc

      - name: fam_t2
        members: 
          tom:
           password: tom_ps
          jane:
           password: jane_ps
        boss: tom
        balance: 102.92
        my_trust: 150
        location: fam_t2_loc

"""


basic_ad2_setup_yaml = f"""

  ad2_setup:
    users:
      - john2
      - katy2

    families:
      - name: fam_t2
        members:
          john2:
            password: john_pass
          katy2:
            password: katy_pass
        boss: john2
        balance: 239.19
        my_trust: 250
        location: ad2_fam_t2
 

"""


fixture_associate_1_yaml = f"""

{basic_ad1_setup_yaml} 

      - name: fam_t3
        members: 
          bill:
           password: bill_ps
          pat:
           password: pat_ps
        boss: bill 
        balance: 2.92
        my_trust: 40
        location: fam_t3_loc

      - name: upper_fam
        level: 1
        members: 
          - '#fa#fam_t1'
          - '#fa#fam_t2'
          - '#fa#fam_t3'
        boss: '#al#alice.fam_t1@www.ad1.com'
        carrier: '#al#pat.fam_t3@www.ad1.com'
        balance: 10.92
        my_trust: 150
        system_trust: 200
        brotherhood_ratio: 0.58
        location: upper_fam_loc


{basic_ad2_setup_yaml} 

"""


fixture_1_yaml = f"""

{basic_ad1_setup_yaml} 
 
  ad2_setup:

    families:
      - name: fam_t2
        members:
          john_al:
            actor: '@john3@www.ad3.com'
            password: john_pass
          katy_al:
            actor: '@katy3@www.ad3.com'
            password: katy_pass
        boss: john_al
        balance: 239.19
        my_trust: 250
        location: ad2_fam_t2
   

  ad3_setup:

    users:
      - john3
      - katy3

    families:
      - name: fam_t3
        members: 
          john_a3:
            actor: john3
            password: john_a3pp
          katy_a3:
            actor: katy3
            password: katy_a3pp
        boss: john_a3
        balance: 63.44
        my_trust: 99
        location: ad3_fam_t3


"""


