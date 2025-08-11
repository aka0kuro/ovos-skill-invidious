# <img src='./res/invidious.png' width='50' height='50' style='vertical-align:bottom'/> Invidious Skill

Invidious OCP Skill - Private Alternative to YouTube

## About

Search videos on Invidious by voice! Invidious is a private and alternative frontend to YouTube that doesn't require cookies or JavaScript.

## Features

- **Automatic instance discovery** from [redirect.invidious.io](https://redirect.invidious.io/)
- Video search through multiple Invidious instances
- Support for music, videos and general content
- Automatic fallback between instances if one fails
- No tracking or cookies
- Natural voice interface
- **Complete support for Spanish (es-ES)**
- **Multiple languages**: English, Spanish, German, Italian

## Examples

### In English
* "play António Variações"
* "search for tutorial videos"
* "find music videos"
* "search invidious for cooking recipes"
* "play spanish music"
* "search for tutorials in english"
* "find cooking recipes"
* "play flamenco"
* "play sevillanas"
* "search for documentaries in english"

## Configuration

You can add queries to the skill configuration that will be pre-fetched when the skill loads.

This populates the featured_media entries + provides fast matching against cached entries.

```javascript
{    
"featured":  ["zz top", "ai covers", "frank sinatra", "tutorial python", "spanish music", "flamenco"]
}
```

## Invidious Instances

The skill automatically discovers available Invidious instances from [redirect.invidious.io](https://redirect.invidious.io/) for maximum reliability:

- **Auto-discovery**: Automatically finds working instances
- **Health checks**: Tests each instance before use
- **Fallback system**: Uses configured instances if auto-discovery fails
- **Dynamic updates**: Gets fresh instance list on each skill load

### Fallback Instances
If auto-discovery fails, these instances are used as backup:
- https://invidious.projectsegfau.org
- https://invidious.slipfox.xyz  
- https://invidious.prvcy.projectsegfau.org
- https://inv.nadeko.net

## Language Support

### Spanish (es-ES)
- Complete vocabulary in Spanish
- Natural commands in Spanish
- Featured queries in Spanish
- Regional configuration for Spain

### Other Languages
- English (en-US) - Fully supported
- German (de-DE) - Basic support
- Italian (it-IT) - Basic support

## Credits
JarbasAl (original YouTube Music skill)
aka0kuro (conversion to Invidious and Spanish support)

## Category
**Entertainment**

## Tags
- invidious
- youtube alternative
- common play
- video
- music
- privacy
- english
- localization
- auto-discovery
