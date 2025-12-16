# Alterra/MtnPowder Home Assistant Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
[![CI][ci-shield]][ci]

[![Buy me a coffee][buymeacoffee-shield]][buymeacoffee]

This Home Assistant custom integration provides comprehensive monitoring for Alterra ski resorts by reading data from the MtnPowder feed (https://mtnpowder.com/feed/). It creates sensors and weather entities to track resort conditions, snow reports, trail status, and weather forecasts.

## Features

### Sensors
The integration creates multiple sensors for each selected resort:

#### Operating Status
- **Operating Status**: Current operational status of the resort

#### Snow Report Data
- **Base Conditions**: Current snow conditions at base
- **Snow Report**: Full text report with updates and announcements
- **Terrain Information**: Open/Total Terrain Acres/Hectares, Open/Total Trails, Lifts, Activities
- **Snow Totals**: Storm Total, Season Total, Base Depth measurements
- **Grooming & Snowmaking**: Active status indicators

#### Mountain Areas
- **Trail Counts**: Open/Total trails for each mountain area (e.g., Glades, Learning Areas, Lower Mountain, etc.)

#### Individual Trails
- **Trail Status**: Open/Closed status for each named trail
- **Trail Details**: Difficulty, snowmaking, grooming, night skiing, moguls, glades, etc.

#### Lifts
- **Lift Status**: Operational status for each lift
- **Lift Details**: Type, capacity, hours, wait times

#### Activities
- **Activity Status**: Open/Closed status for resort activities (golf, hiking, mountain biking, etc.)

#### Update Tracking
- **Updates Today**: Count of successful data updates per day
- **No Updates Today**: Count of times data was unchanged per day

### Weather Entities
For each resort, weather entities are created for the areas at each resort.  For example, at Strattion, these areas would be:

#### Areas Covered
- **Base**: Base area weather conditions
- **Mid Mountain**: Mid-mountain weather conditions
- **Summit**: Summit weather conditions

#### Current Conditions
- **Temperature**: Current temperature in Celsius
- **Humidity**: Relative humidity percentage
- **Wind Speed & Direction**: Wind speed in km/h and bearing
- **Pressure**: Atmospheric pressure in mbar
- **Weather Condition**: Mapped to Home Assistant conditions (sunny, cloudy, snowy, etc.)
- **Dew Point**: Dew point temperature
- **Wind Chill**: Wind chill temperature

#### Weather Forecast
- **5-Day Forecast**: Twice-daily forecasts (daytime/nighttime) for 5 days
- **Temperature**: High/low temperatures
- **Conditions**: Weather conditions for each period
- **Precipitation**: Snowfall amounts converted to mm

## Supported Resorts

This integration supports all Alterra-owned ski resorts that provide data through the MtnPowder JSON feed. The following resorts are currently available:

- **Stratton**
- **Snowshoe**
- **Blue**
- **Tremblant**
- **Winter Park**
- **Steamboat**
- **Stratton Summer**
- **Snowshoe Summer**
- **Blue Summer**
- **Tremblant Summer**
- **Winter Park Summer**
- **Steamboat Summer**
- **Deer Valley**
- **Deer Valley Summer**
- **Aspen Highlands**
- **Aspen Mountain**
- **Buttermilk**
- **Snowmass**
- **Copper Mountain**
- **Eldora**
- **Bear Mountain**
- **Snow Summit**
- **June Mountain**
- **Mammoth Mountain**
- **Palisades Tahoe**
- **Alta**
- **Snowbird**
- **Solitude**
- **Brighton**
- **Jackson Hole**
- **Big Sky**
- **Killington**
- **Sugarbush**
- **Loon Mountain**
- **Sugarloaf**
- **Sunday River**
- **Lake Louise**
- **Mt Norquay**
- **Sunshine Village**
- **Revelstoke**
- **Taos**
- **Summit at Snoqualmie**
- **Crystal Mountain**
- **Cypress Mountain**
- **Boyne Highlands**
- **Boyne Mountain**
- **Niseko Annupuri**
- **Niseko Grand Hirafu**
- **Niseko Hanazano**
- **Niseko Village**
- **Bear Mountain Summer**
- **Snow Summit Summer**
- **Mammoth Mountain Summer**
- **June Mountain Summer**
- **Arapahoe Basin**
- **Pico Mountain**
- **Solitude Summer**
- **Mt Bachelor**
- **Windham Mountain**
- **RED Mountain**
- **Sugarbush Summer**
- **Snowbasin Resort**
- **Chamonix**
- **Tamarack Cross Country Ski Center**
- **Schweitzer**
- **Lotte Arai**
- **Panorama Mountain Resort**
- **Sun Peaks**
- **Grandvilara**
- **Snow Valley**
- **Snow Valley Summer**
- **Alyeska**
- **Blue Mountain (PA)**
- **Camelback**
- **Mt Bueller**
- **Coronet Peak**
- **The Remarkables**
- **Mt Hutt**
- **Thredbo**
- **Valle Nevado**
- **Cortina d'Ampezzo**
- **Kronplatz/Plan de Corones**
- **Alta Badia**
- **Val Gardena/Alpe de Siusi**
- **Val di Fassa/Carezza**
- **Arabba/Marmolada**
- **3 Peaks Dolomites**
- **Val di Fiemme/Obereggen**
- **San Martino di Castrozza/Rolle Pass**
- **Civetta**
- **Kitzbühel**
- **St Moritz**
- **Alpental**
- **Zermatt Matterhorn**
- **Rio Pusteria - Bressanone**
- **Alpe Lusia - San Pellegrino**
- **Sierra at Tahoe**
- **Ischgl**
- **Le Massif**
- **Schweitzer Summer**
- **Mt. T**
- **Nekoma**
- **Yunding Snow Park**
- **Cervino Ski Paradise**
- **Courmayeur Mont Blanc**
- **Espace San Bernardo**
- **Monterosa Ski**
- **Pila**
- **Yakebitaiyama Ski Area**
- **Okushiga Kogen Ski Area**
- **Kumanoyu**
- **Yokoteyama**
- **Sun Valley**
- **Megeve**
- **Mona Yongpyong**
- **Furano Ski Resort**
- **Appi Kogen Resort**
- **Zao Onsen Ski Resort**
- **Bear Mountain / Snow Summit**

The integration automatically discovers available resorts from the feed.

## Installation

### Method 1: Manual Installation
1. Download or clone this repository
2. Copy the `custom_components/mtnpowder` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant
4. Add the integration through the UI:
   - Go to **Settings** > **Devices & Services** > **Add Integration**
   - Search for "MtnPowder" or "Alterra"
   - Select the resorts you want to monitor

### Method 2: HACS (Recommended)
1. Ensure [HACS](https://hacs.xyz/) is installed
2. Add this repository as a custom repository in HACS
3. Install the "Alterra/MtnPowder" integration
4. Restart Home Assistant
5. Add the integration through HACS

## Configuration

### Integration Setup
1. After installation, the integration will appear in your integrations list
2. Click "Add Integration" and select "MtnPowder"
3. Select which resorts you want to monitor from the available list
4. The integration will automatically create all sensors and weather entities for the resort(s) chosen

### Configuration Options
- **Resorts**: Multi-select which Alterra resorts to monitor
- **Update Interval**: How often to check for updates (default: configured in integration)

## Data Sources

- **Primary Feed**: https://mtnpowder.com/feed/
- **Update Method**: Uses HEAD requests to check for changes before downloading full data to reduce bandwidth required. Implements ETag and Last-Modified header comparisons to determine whether or not the feed has changed.

## Requirements

- Home Assistant 2021.1 or later
- Internet connection for feed access
- Python packages: aiohttp, feedparser (automatically installed)

## Troubleshooting

### Common Issues

**No sensors appear after setup:**
- Check that the selected resorts are currently operational and providing data
- Verify internet connectivity
- Check Home Assistant logs for errors

**Weather data not updating:**
- Weather data comes from resort weather stations
- Some areas may not have complete weather data
- Check the resort's website for current conditions

**High update frequency:**
- The integration uses smart caching to avoid unnecessary downloads
- Monitor the "Updates Today" sensor to see actual data refresh frequency

### Debug Logging
Add the following to your `configuration.yaml` to enable debug logging:

```yaml
logger:
  logs:
    custom_components.mtnpowder: debug
```

## Contributing

This integration is developed as a community project. Contributions are welcome!

- Report issues on the GitHub repository
- Submit pull requests for improvements
- Test with additional Alterra resorts

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This integration is not officially affiliated with Alterra Mountain Company or MtnPowder. Use at your own risk.

<!-- Badges -->
[buymeacoffee]: https://www.buymeacoffee.com/stevemurphymsu
[buymeacoffee-shield]: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
[commits-shield]: https://img.shields.io/github/commit-activity/y/stevemurphymsu/homeassistant-mtnpowder.svg?style=for-the-badge
[commits]: https://github.com/stevemurphymsu/homeassistant-mtnpowder/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/stevemurphymsu/homeassistant-mtnpowder.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/stevemurphymsu/homeassistant-mtnpowder.svg?style=for-the-badge
[releases]: https://github.com/stevemurphymsu/homeassistant-mtnpowder/releases
[ci-shield]: https://img.shields.io/github/actions/workflow/status/stevemurphymsu/homeassistant-mtnpowder/ci.yml?style=for-the-badge
[ci]: https://github.com/stevemurphymsu/homeassistant-mtnpowder/actions/workflows/ci.yml
