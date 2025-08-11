# Managing Invidious Instances

This document explains how to add, configure, and manage Invidious instances in the skill.

## Overview

The skill now supports multiple ways to get Invidious instances:

1. **Auto-discovery** from [redirect.invidious.io](https://redirect.invidious.io/)
2. **Custom instances** from configuration
3. **Fallback instances** for reliability

## Adding Instances

### Method 1: Configuration File (Recommended)

Edit `config.json` and add instances to the `custom_instances` array:

```json
{
  "instance_management": {
    "custom_instances": [
      "https://invidious.snopyta.org",
      "https://invidious.kavin.rocks",
      "https://invidious.weblibre.org",
      "https://invidious.nerdvpn.de",
      "https://invidious.sethforprivacy.com"
    ]
  }
}
```

### Method 2: Fallback Instances

Add instances to the main `invidious_instances` array:

```json
{
  "invidious_instances": [
    "https://invidious.projectsegfau.org",
    "https://invidious.slipfox.xyz",
    "https://invidious.prvcy.projectsegfau.org",
    "https://inv.nadeko.net",
    "https://your-custom-instance.com"
  ]
}
```

## Configuration Options

### Instance Management Settings

```json
{
  "instance_management": {
    "auto_discovery": true,           // Enable/disable auto-discovery
    "discovery_url": "https://redirect.invidious.io/",
    "max_instances": 15,              // Maximum total instances
    "fallback_to_config": true,       // Use config if discovery fails
    "health_check_timeout": 5,        // Timeout for health checks
    "custom_instances": []            // Your custom instances
  }
}
```

## Instance Priority

The skill uses instances in this order:

1. **Auto-discovered instances** from redirect.invidious.io
2. **Custom instances** from your configuration
3. **Fallback instances** if needed for reliability

## Finding New Instances

### Official Sources
- [redirect.invidious.io](https://redirect.invidious.io/) - Official redirect service
- [Invidious GitHub](https://github.com/iv-org/invidious) - Official repository
- [Invidious Instances](https://instances.invidious.io/) - Community-maintained list

### Community Lists
- [Invidious Instances Status](https://status.invidious.io/)
- [Invidious Instances List](https://github.com/iv-org/invidious-instances)

## Testing Instances

Before adding an instance, test it:

```bash
# Test if instance is accessible
curl -I "https://your-instance.com/api/v1/stats"

# Test search functionality
curl "https://your-instance.com/api/v1/search?q=test"
```

## Best Practices

### 1. **Diversity**
- Use instances from different regions
- Mix different hosting providers
- Include both large and small instances

### 2. **Reliability**
- Test instances before adding
- Monitor instance health
- Have fallback options

### 3. **Performance**
- Choose instances close to your location
- Avoid overloaded instances
- Use instances with good uptime

## Example Configuration

Here's a complete example with many instances:

```json
{
  "instance_management": {
    "auto_discovery": true,
    "max_instances": 20,
    "custom_instances": [
      "https://invidious.snopyta.org",
      "https://invidious.kavin.rocks",
      "https://invidious.weblibre.org",
      "https://invidious.nerdvpn.de",
      "https://invidious.sethforprivacy.com",
      "https://invidious.prvcy.projectsegfau.org",
      "https://invidious.projectsegfau.org",
      "https://invidious.slipfox.xyz",
      "https://inv.nadeko.net"
    ]
  }
}
```

## Troubleshooting

### Common Issues

1. **Instance not responding**
   - Check if instance is down
   - Verify URL format
   - Test with browser

2. **Too many instances**
   - Reduce `max_instances` in config
   - Remove slow instances
   - Use only reliable instances

3. **Auto-discovery failing**
   - Check internet connection
   - Verify redirect.invidious.io is accessible
   - Use custom instances as fallback

### Logs

Check the skill logs for instance-related information:

```
Found X instances from redirect.invidious.io
Added Y custom instances from configuration
Total instances available: Z
Instance X not available: timeout
```

## Security Considerations

- Only use trusted instances
- Avoid instances with suspicious behavior
- Regularly update your instance list
- Monitor for any security issues

## Support

If you have issues with instances:

1. Check the instance status
2. Test with different instances
3. Review the skill logs
4. Report issues to the instance maintainers 