# zeek-monitor/zeek/local.zeek

# Load standard Zeek scripts
@load base/frameworks/cluster

# Log settings
redef Log::default_rotation_interval = 1 hour;
redef Log::default_archive_time = 1 hour;

# Customize Zeek behavior
redef capture_filters += { ["tcp"] = "tcp" };


###################################################################
# Load default Zeek scripts
#@load base/frameworks/cluster

# Customize Zeek's monitoring behavior as needed
#redef Cluster::nodes += {
#    ["gateway"] = [$node_type=Cluster::Worker, $ip="172.20.0.2", $zone_id="gateway"],};

# Load custom scripts for additional monitoring
#@load protocols/http
#@load protocols/ssl
