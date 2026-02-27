# Hardware & Electronics Diagrams

Diagram types for hardware design, electronics, and wiring documentation.

## Symbolator

Symbolator generates hardware component symbols from VHDL entity declarations.

### ALU Component

```symbolator
library ieee;
use ieee.std_logic_1164.all;

entity ALU is
  port (
    clk    : in std_logic;
    reset  : in std_logic;
    op     : in std_logic_vector(1 downto 0);
    a      : in std_logic_vector(7 downto 0);
    b      : in std_logic_vector(7 downto 0);
    result : out std_logic_vector(7 downto 0);
    carry  : out std_logic;
    zero   : out std_logic
  );
end entity;
```

### UART Transmitter

```symbolator
library ieee;
use ieee.std_logic_1164.all;

entity uart_tx is
  port (
    clk       : in  std_logic;
    reset     : in  std_logic;
    tx_data   : in  std_logic_vector(7 downto 0);
    tx_start  : in  std_logic;
    tx_serial : out std_logic;
    tx_busy   : out std_logic;
    tx_done   : out std_logic
  );
end entity;
```

## WireViz

WireViz creates wiring harness documentation from YAML descriptions.

### Serial Cable

```wireviz
connectors:
  X1:
    type: D-Sub
    subtype: female
    pincount: 9
    pins: [1, 2, 3, 4, 5]
    pinlabels: [GND, TX, RX, VCC, EN]
  X2:
    type: Molex KK 254
    subtype: female
    pincount: 4
    pins: [1, 2, 3, 4]
    pinlabels: [GND, Signal, VCC, EN]

cables:
  W1:
    gauge: 0.25 mm2
    length: 0.3
    color_code: DIN
    wirecount: 4
    colors: [BK, RD, GN, YE]

connections:
  -
    - X1: [1, 2, 4, 5]
    - W1: [1, 2, 3, 4]
    - X2: [1, 2, 3, 4]
```

### Sensor Harness

```wireviz
connectors:
  MCU:
    type: Pin Header
    subtype: male
    pincount: 6
    pins: [1, 2, 3, 4, 5, 6]
    pinlabels: [3V3, GND, SDA, SCL, INT, RST]
  Sensor1:
    type: JST-PH
    subtype: female
    pincount: 4
    pins: [1, 2, 3, 4]
    pinlabels: [VCC, GND, SDA, SCL]
  Sensor2:
    type: JST-PH
    subtype: female
    pincount: 4
    pins: [1, 2, 3, 4]
    pinlabels: [VCC, GND, SDA, SCL]

cables:
  C1:
    wirecount: 4
    gauge: 0.14 mm2
    length: 0.15
    colors: [RD, BK, YE, GN]
  C2:
    wirecount: 4
    gauge: 0.14 mm2
    length: 0.25
    colors: [RD, BK, YE, GN]

connections:
  -
    - MCU: [1, 2, 3, 4]
    - C1: [1, 2, 3, 4]
    - Sensor1: [1, 2, 3, 4]
  -
    - MCU: [1, 2, 3, 4]
    - C2: [1, 2, 3, 4]
    - Sensor2: [1, 2, 3, 4]
```
