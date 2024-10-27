# USER PLANE Testing
I created this setup to monitor simulated traffic generated with Ostinato on a single isloated upf using a simulated PFCP session. It allows for testing Zeek configurations for user traffic.

## State: Not Finished - GOT LAZY and did not really need it in the end
Follow this:
https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-upf-vpp/-/blob/master/docs/UPF_BRACKET_TESTING.md?ref_type=heads
                               ------------------------
                               |    PFCP Simulator    |
                               ------------------------
                                          |
                                          | N4
  --------------------       N3     -------------
  |                  |   ---------> |           |
  | Traffic Generaor |              |    UPF    |
  |                  |   <--------- |           |
  --------------------        N6    -------------

can switch out the useless traffic genrator with Ostinato: look at the Ostinato install instructions located under /custom_elements/prototype_v6_ueransim/install.d. Unfortunately requires Host for GUI with Ostinato also installed.

Can either adopt the gateway configuration from /docker/hybrid, or try intstall filebeat and zeek like it is done in /custom_elements/filebeat|zeek_v6 and /docker/zeek_testing... GOOD LUCK - Should actually be easy