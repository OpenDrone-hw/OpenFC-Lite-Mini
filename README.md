# OpenFC-Lite-Mini

Open source Betaflight flight controller built on the RP2354A, 20 x 20 mm
mounting pattern, part of the incutec OpenDrone line. Motor outputs are
signal-level DShot to an external 4-in-1 ESC: no onboard motor drivers.

<p>
<img src="images/openfc-lite-mini-rev2-top.png" width="400" alt="OpenFC-Lite-Mini top" />
<img src="images/openfc-lite-mini-rev2-bottom.png" width="400" alt="OpenFC-Lite-Mini bottom" />
</p>

[![Status](https://img.shields.io/badge/status-alpha-e08c00)](https://github.com/OpenDrone-hw/.github/blob/main/CONTRIBUTING.md#the-life-of-a-project)
[![Shop](https://img.shields.io/badge/shop-opendrone.be-ffb700)](https://opendrone.be/products/openfc-lite)
[![Discord](https://img.shields.io/badge/Discord-%23flight--controllers-5865F2?logo=discord&logoColor=white)](https://discord.com/channels/1494019459822653512/1494783056026796262)
[![Video](https://img.shields.io/badge/YouTube-How%20Flight%20Controllers%20Work-FF0000?logo=youtube&logoColor=white)](https://www.youtube.com/watch?v=XDYZoMRJFeQ)
[![OSHWA](https://img.shields.io/badge/OSHWA-BE000027-0099b0)](https://certification.oshwa.org/be000027.html)

Maintained by [@Just4Stan](https://github.com/Just4Stan).

## Specifications

| | |
|---|---|
| Firmware | Betaflight |
| MCU | RP2354A |
| IMU | BMI270 |
| Barometer | None |
| Blackbox | microSD |
| OSD | Analog and digital |
| UARTs | 3 |
| Motor outputs | 4x DShot, bidirectional |
| RX | External, CRSF or SBUS |
| Input | 3-6S LiPo (9.0-25.2 V) |
| BEC | 10 V switchable + 5 V always-on, 3 A |
| Current sense | Yes |
| USB | USB-C |
| Mounting | 20 x 20 mm, 3.0 mm holes |
| Dimensions | 26.9 x 26.9 mm |
| PCB | 6-layer, 1.6 mm |

Technical write-up, part list and layout constraints: [AGENTS.md](AGENTS.md).

## In the line

What pairs with what, and what is available:
[opendrone.be](https://opendrone.be).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Hardware licensed under [CERN-OHL-S-2.0](https://ohwr.org/cern_ohl_s_v2.txt),
see [LICENSE](LICENSE).
