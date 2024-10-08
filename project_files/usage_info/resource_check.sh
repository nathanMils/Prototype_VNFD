

sudo python3 resource_check.py -c $VNF -d 300 -i 5 -n "$VNF idle" --zapier-webhook "https://hooks.zapier.com/hooks/catch/20350848/2mcrrua/"

sudo python3 resource_check.py -c $VNF -d 600 -i 5 -n "$VNF Load" --zapier-webhook "https://hooks.zapier.com/hooks/catch/20350848/2mcrrua/"

