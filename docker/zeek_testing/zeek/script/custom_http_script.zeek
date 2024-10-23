# custom_http_script.zeek
module CaptureAllHTTP;

export {
    global log_http: event(rec: HTTP::Info);  # Use the existing HTTP::Info type
}

# Initialize the script and create a logging stream
event zeek_init() &priority=5 {
    Log::create_stream(HTTP::LOG, [$columns=HTTP::Info, $path="http_requests"]);
}

# Capture HTTP requests
event http_request(c: connection, method: string, original_URI: string, 
                   unescaped_URI: string, version: string) &priority=5 {
    local rec: HTTP::Info;   # Use the Info type from the HTTP module
    rec$ts = network_time();  # Set the timestamp
    rec$uid = c$uid;          # Set the connection's unique ID
    rec$method = method;      # Set the HTTP method
    rec$uri = unescaped_URI;  # Set the unescaped URI
    rec$host = c$http$host;   # Set the Host header
    
    Log::write(HTTP::LOG, rec);  # Write the record to the log
}

# Capture HTTP replies
event http_reply(c: connection, version: string, code: count, reason: string) &priority=5 {
    if (c?$http) {
        c$http$status_code = code;  # Store the status code in the HTTP record
        c$http$status_msg = reason;  # Store the status message in the HTTP record
    }
}

# Capture HTTP headers
event http_header(c: connection, is_orig: bool, name: string, value: string) &priority=5 {
    if (is_orig && name == "HOST") {
        c$http$host = value;  # Store the Host header value
    }
}
