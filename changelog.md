# Changelog

20200903  
added "-C" for Context, needed for SmartCloud-1   
added possibility to check IPS Version on managed gateways via the Management Server (Api Call "run-script")  
20200906  
added optional arg "-M" for monitoring Management Servers IPS Version only and "-v" for verbosity and debugging  
20201024  
added and improved error handling  
- when SMS did not get an IPS version update or was not able to fetch recent version  
- when SMS cannot reach a gateway  
- added more logging outputs at verbose executing (-v)  
- for checking on "On Premise" SMS, no argument "-C" needed

