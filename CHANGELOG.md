# Changelog

## [1.1.0] - 2024-12-19

### 🚀 New Feature - Automatic Instance Discovery

#### ✨ New Features
- **Automatic instance discovery** from [redirect.invidious.io](https://redirect.invidious.io/)
- **Dynamic instance management** - No more hardcoded instances
- **Real-time health checks** for all discovered instances
- **Smart fallback system** to configured instances if auto-discovery fails

#### 🔄 Major Changes
- Added `get_invidious_instances()` method for dynamic discovery
- Added `parse_invidious_redirect()` method to parse instance URLs
- Enhanced configuration with `instance_management` section
- Improved logging for instance discovery process

#### 🏗️ Architectural Changes
- Instances are now discovered at runtime instead of hardcoded
- Fallback mechanism ensures reliability even if discovery fails
- Configurable discovery parameters (timeout, max instances, etc.)

#### 📁 Configuration Updates
- Added `instance_management` section to `config.json`
- Configurable auto-discovery settings
- Fallback instance configuration maintained

---

## [1.0.0] - 2024-12-19

### 🚀 New Major Version - Conversion to Invidious

#### ✨ New Features
- **Complete conversion** from YouTube Music to Invidious
- **Multiple instances** of Invidious with automatic fallback
- **Video support** in addition to music
- **Flexible configuration** through config.json file
- **Improved scoring system** for more relevant results

#### 🔄 Major Changes
- Replaced `tutubo` with direct Invidious API
- Changed `YoutubeMusicSkill` to `InvidiousSkill`
- Updated vocabulary from "youtube" to "invidious"
- Improved error handling and timeouts
- Added support for configurable settings

#### 🏗️ Architectural Changes
- New `InvidiousVideo` class for video representation
- Fallback system between Invidious instances
- Configuration loading from JSON file
- Better logging and debugging

#### 📁 New Files
- `config.json` - Skill configuration
- `test_invidious.py` - Test script
- `DOCUMENTATION.md` - Complete documentation
- `locale/en-us/invidious_skill.voc` - Specific vocabulary

#### 🔧 Technical Improvements
- Support for multiple media types (MUSIC, VIDEO, GENERIC)
- Configurable search parameters
- Configurable result limits
- Better exception handling

#### 📚 Documentation
- README completely updated in English
- Detailed technical documentation
- Usage examples and configuration
- Troubleshooting guide

#### 🗑️ Removed
- `tutubo` dependency
- YouTube Music specific classes
- Obsolete YouTube vocabulary

---

## [0.1.7] - 2023-XX-XX

### 🎵 Original YouTube Music Skill
- YouTube Music search
- Album and playlist support
- OVOS Common Play integration

---

## Migration Notes

### For Existing Users
1. **Uninstall** previous skill version
2. **Install** new Invidious version
3. **Configure** preferred instances in `config.json`
4. **Update** vocabulary from "youtube" to "invidious"

### Compatibility
- ✅ OVOS Common Play
- ✅ Multiple platforms (ARM, x86, etc.)
- ✅ Python 3.7+
- ❌ YouTube Music specific (replaced by Invidious)

### Migration Benefits
- **Greater privacy** - No Google tracking
- **Better reliability** - Multiple instances
- **More functionality** - Support for videos and music
- **Flexible configuration** - User customizable

---

## Credits

### Authors
- **JarbasAl** - Original YouTube Music skill author
- **aka0kuro** - Conversion to Invidious and Spanish support

### Contributions
- Complete codebase conversion
- Invidious API implementation
- Instance fallback system
- Complete multi-language support
- Detailed technical documentation
- Examples and usage guides
