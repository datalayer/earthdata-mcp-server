# NASA Earthdata Authentication

To access NASA Earthdata resources, you need to authenticate with NASA's Earthdata Login system. The tools in this server handle authentication automatically, but you'll need to provide credentials when prompted.

### Getting a NASA Earthdata Account

1. **Create an Account**: Visit [https://urs.earthdata.nasa.gov/](https://urs.earthdata.nasa.gov/) and click "Register"
2. **Fill out the registration form** with your information
3. **Verify your email** address by clicking the link in the confirmation email
4. **Log in** to your account at [https://urs.earthdata.nasa.gov/](https://urs.earthdata.nasa.gov/)

### Authentication Methods

The earthaccess library (used by this server) supports several authentication methods:

#### 1. Interactive Login (Recommended for Development)
When using the server, the first time you access NASA data, you'll be prompted to log in:

```python
# This happens automatically when using download_earth_data_granules
# or when the earthaccess library is first used
auth = earthaccess.login()
```

The system will prompt you for:
- **Username**: Your NASA Earthdata username  
- **Password**: Your NASA Earthdata password

#### 2. Environment Variables (Recommended for Production)
Set these environment variables to avoid interactive prompts:

```bash
export EARTHDATA_USERNAME="your_username"
export EARTHDATA_PASSWORD="your_password"
```

#### 3. .netrc File (Alternative Method)
Create a `.netrc` file in your home directory:

```bash
# ~/.netrc
machine urs.earthdata.nasa.gov
login your_username
password your_password
```

**Important**: Make sure the `.netrc` file has proper permissions:
```bash
chmod 600 ~/.netrc
```

### Testing Your Authentication

You can test your authentication by running a simple earthaccess command:

```python
import earthaccess

# Test authentication
auth = earthaccess.login()
if auth:
    print("✅ Authentication successful!")
    
    # Test data access
    results = earthaccess.search_datasets(keyword="sea level", count=1)
    print(f"Found {len(results)} datasets")
else:
    print("❌ Authentication failed")
```

### Security Best Practices

- **Never commit credentials** to version control
- **Use environment variables** in production environments
- **Keep your .netrc file private** with proper file permissions
- **Regularly update your password** for security

### Troubleshooting Authentication

If you encounter authentication issues:

1. **Verify your credentials** at [https://urs.earthdata.nasa.gov/](https://urs.earthdata.nasa.gov/)
2. **Check for account suspension** - NASA may temporarily suspend accounts for security reasons
3. **Clear cached credentials** by deleting `~/.earthaccess_config` if it exists
4. **Try interactive login** even if using environment variables to debug the issue

For more details, see the [earthaccess authentication documentation](https://earthaccess.readthedocs.io/en/latest/quick-start/#authentication).
