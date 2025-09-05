# NASA Earthdata Authentication

To access NASA Earthdata resources, you need to authenticate with NASA's Earthdata Login system. The tools in this server handle authentication automatically, but you'll need to provide environment variables with your Earthdata credentials.

### Getting a NASA Earthdata Account

1. **Create an Account**: Visit [https://urs.earthdata.nasa.gov/](https://urs.earthdata.nasa.gov/) and click "Register"
2. **Fill out the registration form** with your information
3. **Verify your email** address by clicking the link in the confirmation email
4. **Log in** to your account at [https://urs.earthdata.nasa.gov/](https://urs.earthdata.nasa.gov/)

### Authentication Methods

The [earthaccess](https://pypi.org/project/earthaccess/) library is used to download data from NASA Earthdata.
You need to provide your Earthdata Login credentials: `EARTHDATA_USERNAME` and `EARTHDATA_PASSWORD` via environment variables.
