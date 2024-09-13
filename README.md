# WebOrion Protector Demo Control Panel
This application is created to hold the different web application vulnerabilities exploits and to showcase the WebOrion Protetor WAF capabilities in deterring these threats. 

## Objective
Firstly, because the vulnerable applications are hosted in the cloud, leaving them accessible to the public could make them targets for attackers. They might exploit our cloud instances to access sensitive information or use them to launch malicious attacks on other public web applications. As a result, access to these vulnerable applications is restricted to the control panel, which requires login credentials.

Secondly, it features demo guides that are valuable for replicating web application exploits to highlight the capabilities of the WebOrion Protector WAF. These guides will also include the necessary payloads for executing the exploits.

## Solution
In this application, we use Nginx auth validator [here](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-subrequest-authentication/). The idea is to create a proxy `/auth`
that will constantly check if the users are logged in and verified. This authenticator will be positioned above the various server blocks that redirect to the vulnerable applications. In the scenario that it is unable to be verified, it will always be redirected to a log in page. This prevents malicious attackers from accessing the control panel. 

## Pre-requisite

### Docker
The control panel application is containerized

### Juice Shop
Run juice shop on port `3000`. We are currently running the juice shop full version (not docker). Refer to [this](https://github.com/juice-shop/juice-shop/releases/tag/v17.1.1) for the release versions of juice shop.

### Web shell
Run web shell on port `8000`. Currently we use a very simple version of webshell, [qsd.php](https://github.com/JohnTroony/php-webshells/blob/master/Collection/qsd-backdoor.php). For more advance features, there is a [wso shell](https://github.com/mIcHyAmRaNe/wso-webshell). 
- We are not using the wso shell because of the current limitation of how CRS detects these type of attacks

## Running the application
```
git clone https://github.com/Cloudsine-weborion/wpop-presales-login-webapp.git
```

```
# building the application
make app

# running the app
make run

# remove all relevant app container and images
make remove
```
