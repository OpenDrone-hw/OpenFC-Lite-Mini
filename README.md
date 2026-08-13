# OpenFC-Lite-Mini

Open source Betaflight flight controller built on the RP2354A, 20 x 20 mm mounting
pattern, part of the incutec OpenDrone line. Motor outputs are signal-level
DShot to an external 4-in-1 ESC: no onboard motor drivers, no barometer, no
integrated receiver.

<p>
<img src="images/openfc-lite-mini-rev2-top.png" width="400" alt="OpenFC-Lite-Mini top" />
<img src="images/openfc-lite-mini-rev2-bottom.png" width="400" alt="OpenFC-Lite-Mini bottom" />
</p>

|  |  |
|---|---|
| Size | 20 x 20 mm mounting pattern |
| MCU | RP2354A |
| Blackbox | microSD |
| Firmware | [Betaflight](https://github.com/betaflight/betaflight) |

<a href="https://certification.oshwa.org/be000027.html">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="images/oshwa-certified-dark.svg" />
    <img src="images/oshwa-certified.svg" width="160" alt="OSHWA Certified Open Source Hardware, BE000027" />
  </picture>
</a>

Certified open source hardware by the [Open Source Hardware Association](https://www.oshwa.org/),
OSHWA UID **[BE000027](https://certification.oshwa.org/be000027.html)**.

## In the line

- [OpenFC-Lite](https://github.com/OpenDrone-hw/OpenFC-Lite): 30.5 x 30.5 mm, RP2354B, bigger pads and more I/O.
- [OpenESC-20x20](https://github.com/OpenDrone-hw/OpenESC-20x20): the 20 x 20 mm 4-in-1 ESC this stacks with. This board has no motor
  drivers, so it needs one.
- [OpenRX](https://github.com/OpenDrone-hw/OpenRX): ExpressLRS receivers for the
  4-pin receiver connector.

## Get one

[opendrone.be](https://opendrone.be)

Build videos: [JustFPV](https://www.youtube.com/@justfpv1432)

## Contributing

Issues and pull requests are welcome on any repo. KiCad files cannot be merged,
so say what you intend to change before you do, on
[Discord](https://discord.gg/v3sWmTcx3R).

The design itself, the part list and the layout constraints are in
[AGENTS.md](AGENTS.md). How everything works:
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

Hardware licensed under [CERN-OHL-S-2.0](https://ohwr.org/cern_ohl_s_v2.txt),
see [LICENSE](LICENSE).
