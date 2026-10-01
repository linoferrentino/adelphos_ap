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


single_world_yaml = """

    instances:
        -  name: adelphos
           host: www.adelphos.it
           root: lino
           password: super_secret

"""

fixture_writers_poets_wrong = """

  adelphos_setup:
    
    users:
        - udante
        - ugiacomo
        - ualessandro
         

    families:

       - name: alighieri
         members: 
           dante:
             password: beatrice
             actor: udante
         boss: dante 
         balance: 0
         my_trust: 10
         
       - name: leopardi 
         members: 
           giacomo:
             password: silvia
             actor: ugiacomo
         boss: dante 
         balance: 0
         my_trust: 10


"""

fixture_1_single = """

  adelphos_setup:
    
    users:

    families:


"""

fixture_2_complex_parametric = """

  adelphos_setup:
    
    users:

      - a0
      - a1
      - a2
      - a3
      - a4
      - a5
      - a6
      - a7
      - b0
      - b1
      - b2
      - b3
      - b4
      - b5
      - b6
      - b7
      - c0
      - c1
      - c2
      - c3
      - c4
      - c5
      - c6
      - c7

    families:

      - name: f0_l0
        members: 
          a0:
           password: a0ps
          b0:
           password: b0ps
          c0:
           password: c0ps
        boss: a0
        balance: 0
        my_trust: 5
        location: f0_l0_loc

      - name: f1_l0
        members: 
          a1:
           password: a1ps
          b1:
           password: b1ps
          c1:
           password: c1ps
        boss: a1
        balance: 0
        my_trust: 5
        location: f1_l0_loc

      - name: f2_l0
        members: 
          a2:
           password: a2ps
          b2:
           password: b2ps
          c2:
           password: c2ps
        boss: a2
        balance: 0
        my_trust: 5
        location: f2_l0_loc

      - name: f3_l0
        members: 
          a3:
           password: a3ps
          b3:
           password: b3ps
          c3:
           password: c3ps
        boss: a3
        balance: 0
        my_trust: 5
        location: f3_l0_loc

      - name: f4_l0
        members: 
          a4:
           password: a4ps
          b4:
           password: b4ps
          c4:
           password: c4ps
        boss: a4
        balance: 0
        my_trust: 5
        location: f4_l0_loc

      - name: f5_l0
        members: 
          a5:
           password: a5ps
          b5:
           password: b5ps
          c5:
           password: c5ps
        boss: a5
        balance: 0
        my_trust: 5
        location: f5_l0_loc


      - name: f6_l0
        members: 
          a6:
           password: a6ps
          b6:
           password: b6ps
          c6:
           password: c6ps
        boss: a6
        balance: 0
        my_trust: 5
        location: f6_l0_loc

      - name: f7_l0
        members: 
          a7:
           password: a7ps
          b7:
           password: b7ps
          c7:
           password: c7ps
        boss: a7
        balance: 0
        my_trust: 50
        location: f7_l0_loc

      - name: f0-1_l1
        level: 1
        members: 
          - '#fa#f0_l0'
          - '#fa#f1_l0'
        boss: '{_boss_f0_1_l1_}'
        carrier: '#al#c0.f0_l0'
        balance: 0
        my_trust: 10
        system_trust: 10
        brotherhood_ratio: 0.618
        location: upper_fam_loc

      - name: f2-3_l1
        level: 1
        members: 
          - '#fa#f2_l0'
          - '#fa#f3_l0'
        boss: '#al#b2.f2_l0'
        carrier: '#al#c2.f2_l0'
        balance: 0
        my_trust: 10
        system_trust: 10
        brotherhood_ratio: 0.618
        location: upper_fam_loc

      - name: f0-3_l2
        level: 2
        members: 
          - '#fa#f0-1_l1'
          - '#fa#f2-3_l1'
        boss: '#al#b3.f3_l0'
        carrier: '#al#c3.f3_l0'
        balance: 0
        my_trust: 10
        system_trust: 10
        brotherhood_ratio: 0.382
        location: upper_fam_loc


      - name: f4-5_l1
        level: 1
        members: 
          - '#fa#f4_l0'
          - '#fa#f5_l0'
        boss: '#al#b4.f4_l0'
        carrier: '#al#c4.f4_l0'
        balance: 0
        my_trust: 10
        system_trust: 10
        brotherhood_ratio: 0.618
        location: upper_fam_loc

      - name: f6-7_l1
        level: 1
        members: 
          - '#fa#f6_l0'
          - '#fa#f7_l0'
        boss: '#al#b6.f6_l0'
        carrier: '#al#c6.f6_l0'
        balance: 0
        my_trust: 10
        system_trust: 10
        brotherhood_ratio: 0.618
        location: upper_fam_loc

      - name: f4-7_l2
        level: 2
        members: 
          - '#fa#f4-5_l1'
          - '#fa#f6-7_l1'
        boss: '#al#b7.f7_l0'
        carrier: '{_carrier_f4-7_l2}'
        balance: 0
        my_trust: 10
        system_trust: 10
        brotherhood_ratio: 0.382
        location: upper_fam_loc

      - name: f0-7_l3
        level: 3
        members: 
          - '#fa#f0-3_l2'
          - '#fa#f4-7_l2'
        boss: '#al#a0.f0_l0'
        carrier: '#al#c0.f0_l0'
        balance: 0
        my_trust: 10
        system_trust: 10
        brotherhood_ratio: 0.236
        location: upper_fam_loc


"""

fixture_2_complex_ok_vals = {

    '_boss_f0_1_l1_': '#al#b0.f0_l0',
    '_carrier_f4-7_l2' : '#al#c7.f7_l0',
}


fixture_2_complex_wrong_boss = {

    '_boss_f0_1_l1_': '#al#b2.f2_l0',
    '_carrier_f4-7_l2' : '#al#c7.f7_l0',

}

fixture_2_complex_wrong_carrier = {

    '_boss_f0_1_l1_': '#al#b0.f0_l0',
    '_carrier_f4-7_l2' : '#al#c1.f1_l0',

}
